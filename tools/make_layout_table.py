"""
Dressmaker - DEV ONLY: build translation/layout_patch.json, the byte table that
patch_layout.py (and the installer) applies. Run it again after every game update.

    pip install UnityPy TypeTreeGeneratorAPI
    python make_layout_table.py "<GAME>"

Reads the ORIGINAL files from <GAME>\\uk_backup\\ when they are there (otherwise from
Dressmaker_Data), and the game's Managed DLLs to generate the TextMeshPro field layout
(these files carry no type information).

A change is put in the table only if:
  1. its target is found by object path, and the current settings are the expected ones;
  2. re-encoding the unmodified object reproduces its original bytes exactly;
  3. the patched object keeps its length and changes at most 16 bytes.
Each field is diffed on its own, so every table entry names the field it changes.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "translation", "layout_patch.json")
WRAP_NONE, WRAP_NORMAL = 0, 1
OVERFLOW_OVERFLOW, OVERFLOW_ELLIPSIS = 0, 1
MAX_CHANGED_BYTES = 16

TARGETS = [
    {
        "name": "Inventory list name: wrap, auto-size 13-18 pt",
        "file": "sharedassets2.assets",
        "path": "InventoryDisplayItem/Label/Name",
        "expect": {"m_fontSize": 18.0, "m_enableAutoSizing": 0, "m_TextWrappingMode": WRAP_NONE,
                   "m_overflowMode": OVERFLOW_ELLIPSIS},
        "set": {"m_enableAutoSizing": 1, "m_fontSizeMin": 13.0, "m_fontSizeMax": 18.0,
                "m_TextWrappingMode": WRAP_NORMAL},
    },
    {
        "name": "Cutting room fabric name: auto-size 18-36 pt",
        "file": "level2",
        "path": "CuttingRoom/BottomPanel/Canvas/Panel/NameDescPanel/Name",
        "expect": {"m_fontSize": 36.0, "m_enableAutoSizing": 0, "m_TextWrappingMode": WRAP_NONE,
                   "m_overflowMode": OVERFLOW_OVERFLOW},
        "set": {"m_enableAutoSizing": 1, "m_fontSizeMin": 18.0, "m_fontSizeMax": 36.0},
    },
]


def make_generator(managed, unity_version):
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    gen = TypeTreeGenerator(unity_version)
    for name in sorted(os.listdir(managed)):
        if name.endswith(".dll"):
            try:
                with open(os.path.join(managed, name), "rb") as f:
                    gen.load_dll(f.read())
            except AssertionError:
                pass  # duplicate copies of system assemblies (e.g. Yarn.System.*) fail to load
    return gen


def hierarchy(go):
    names, t = [go.m_Name], None
    for c in go.m_Component:
        obj = c.component.deref()
        if obj.type.name in ("RectTransform", "Transform"):
            t = obj.read(check_read=False)
            break
    while t is not None and t.m_Father and t.m_Father.m_PathID:
        t = t.m_Father.deref().read(check_read=False)
        names.append(t.m_GameObject.deref().read(check_read=False).m_Name)
    return "/".join(reversed(names))


def encode(tree, node, obj):
    from UnityPy.helpers import TypeTreeHelper
    from UnityPy.streams import EndianBinaryWriter
    writer = EndianBinaryWriter(endian=obj.reader.endian)
    TypeTreeHelper.write_typetree(tree, node, writer, obj.assets_file)
    return writer.bytes


def table_for_file(src, data_dir, targets):
    import UnityPy
    # script names live in globalgamemanagers.assets: load the game's copy alongside (read only)
    env = UnityPy.load(src, os.path.join(data_dir, "globalgamemanagers.assets"))
    base = os.path.basename(src)
    mine = [o for o in env.objects if os.path.basename(o.assets_file.name) == base]
    gen = make_generator(os.path.join(data_dir, "Managed"), mine[0].assets_file.unity_version)
    node = gen.get_nodes_up("Unity.TextMeshPro", "TMPro.TextMeshProUGUI")
    data = open(src, "rb").read()
    found = {}
    for obj in mine:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            mb = obj.read(check_read=False)
            if mb.m_Script.deref().read(check_read=False).m_ClassName != "TextMeshProUGUI":
                continue
            path = hierarchy(mb.m_GameObject.deref().read(check_read=False))
        except Exception:
            continue
        for t in targets:
            if path == t["path"] or path.endswith("/" + t["path"]):
                found.setdefault(t["path"], []).append(obj)
    patches = []
    for t in targets:
        objs = found.get(t["path"], [])
        if len(objs) != 1:
            sys.exit(f"{t['name']}: found {len(objs)} matching objects (expected 1)")
        obj = objs[0]
        raw, start = obj.get_raw_data(), obj.byte_start
        if data[start:start + len(raw)] != raw:
            sys.exit(f"{t['name']}: object bytes not at their offset")
        tree = obj.read_typetree(node, check_read=False)
        if encode(tree, node, obj) != raw:
            sys.exit(f"{t['name']}: field layout does not round-trip for this game version")
        wrong = {k: tree.get(k) for k, v in t["expect"].items() if tree.get(k) != v}
        if wrong:
            sys.exit(f"{t['name']}: settings differ from the expected originals {wrong}")
        edits, total = [], bytearray(raw)
        for field, value in t["set"].items():
            one = dict(tree, **{field: value})
            new = encode(one, node, obj)
            if len(new) != len(raw):
                sys.exit(f"{t['name']}: changing {field} changes the object size")
            diff = [i for i in range(len(raw)) if raw[i] != new[i]]
            if not diff:
                continue  # already has that value
            lo, hi = diff[0], diff[-1] + 1
            edits.append({"field": field, "value": value, "offset": start + lo,
                          "old": raw[lo:hi].hex(), "new": new[lo:hi].hex()})
            total[lo:hi] = new[lo:hi]
        changed = sum(a != b for a, b in zip(raw, total))
        if not 0 < changed <= MAX_CHANGED_BYTES:
            sys.exit(f"{t['name']}: {changed} bytes would change")
        if bytes(total) != encode(dict(tree, **t["set"]), node, obj):
            sys.exit(f"{t['name']}: per-field edits do not add up to the full change")
        patches.append({"name": t["name"], "path": t["path"], "path_id": obj.path_id,
                        "object_offset": start, "object_size": len(raw),
                        "object_sha256": hashlib.sha256(raw).hexdigest(), "edits": edits})
        print(f"  {t['name']}: {len(edits)} fields, {changed} bytes")
    return {"file_size": len(data), "file_sha256": hashlib.sha256(data).hexdigest(), "patches": patches}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    game = sys.argv[1]
    data_dir = os.path.join(game, "Dressmaker_Data")
    backup = os.path.join(game, "uk_backup")
    table = {"note": "Generated by tools/make_layout_table.py from the original game files. "
                     "Offsets are absolute file offsets; old/new are hex bytes.", "files": {}}
    for base in sorted({t["file"] for t in TARGETS}):
        src = os.path.join(backup, base)
        if not os.path.isfile(src):
            src = os.path.join(data_dir, base)
        print(f"{base} ({src}):")
        table["files"][base] = table_for_file(src, data_dir, [t for t in TARGETS if t["file"] == base])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"Saved {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
