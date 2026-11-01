"""
Dressmaker - let two item-name labels fit longer (Ukrainian) names.

  * Inventory list name (sharedassets2.assets, InventoryDisplayItem/Label/Name):
    wrap to 2 lines and auto-size 13-18 pt (was: one line, 18 pt, cut off with "...").
  * Cutting room fabric name (level2, .../NameDescPanel/Name):
    auto-size 18-36 pt (was: fixed 36 pt, overflowing the panel).

Usage:
    python patch_layout.py "<GAME>\\Dressmaker_Data\\level2" "<GAME>\\Dressmaker_Data\\sharedassets2.assets" --managed "<GAME>\\Dressmaker_Data\\Managed"

Writes <file>.uk next to each input (an unchanged copy if nothing could be patched).
The inputs may be backups elsewhere; script names are read from the game's own
globalgamemanagers.assets next to the Managed folder.
Needs:  pip install UnityPy TypeTreeGeneratorAPI

These files carry no type information, so the field layout is generated from the
game's own Managed DLLs. Every change is guarded, and a target is skipped (never
half-written) unless:
  1. it is found by its object path, and its current settings are the ones expected;
  2. re-encoding the unmodified object reproduces its original bytes exactly;
  3. the patched object has the same length and differs in only a few bytes.
The new bytes are written in place at the object's offset; nothing else in the
file is re-serialized.
"""
import argparse
import hashlib
import os
import shutil
import sys

WRAP_NONE, WRAP_NORMAL = 0, 1
OVERFLOW_OVERFLOW, OVERFLOW_ELLIPSIS = 0, 1
MAX_CHANGED_BYTES = 16

TARGETS = [
    {
        "name": "Inventory list name",
        "file": "sharedassets2.assets",
        "path": "InventoryDisplayItem/Label/Name",
        "expect": {"m_fontSize": 18.0, "m_enableAutoSizing": 0, "m_TextWrappingMode": WRAP_NONE,
                   "m_overflowMode": OVERFLOW_ELLIPSIS},
        "set": {"m_enableAutoSizing": 1, "m_fontSizeMin": 13.0, "m_fontSizeMax": 18.0,
                "m_TextWrappingMode": WRAP_NORMAL},
    },
    {
        "name": "Cutting room fabric name",
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


def patch_file(src, managed, targets, log=print):
    """Return the number of targets patched; writes src + '.uk'."""
    import UnityPy
    out = src + ".uk"
    shutil.copyfile(src, out)
    if not targets:
        return 0
    # script names live in globalgamemanagers.assets: load the game's copy alongside (read only)
    ggm = os.path.join(os.path.dirname(os.path.abspath(managed)), "globalgamemanagers.assets")
    env = UnityPy.load(src, ggm)
    mine = [o for o in env.objects if os.path.basename(o.assets_file.name) == os.path.basename(src)]
    if not mine:
        log(f"  SKIP: no objects read from {os.path.basename(src)}")
        return 0
    gen = make_generator(managed, mine[0].assets_file.unity_version)
    node = gen.get_nodes_up("Unity.TextMeshPro", "TMPro.TextMeshProUGUI")
    data = bytearray(open(src, "rb").read())
    todo = {t["path"]: t for t in targets}
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
        for want, t in todo.items():
            if path == want or path.endswith("/" + want):
                found.setdefault(want, []).append(obj)
    done = 0
    for want, t in todo.items():
        objs = found.get(want, [])
        if len(objs) != 1:
            log(f"  SKIP {t['name']}: found {len(objs)} matching objects (expected 1)")
            continue
        obj = objs[0]
        raw = obj.get_raw_data()
        start = obj.byte_start
        if bytes(data[start:start + len(raw)]) != raw:
            log(f"  SKIP {t['name']}: object bytes not found at their offset")
            continue
        tree = obj.read_typetree(node, check_read=False)
        if encode(tree, node, obj) != raw:
            log(f"  SKIP {t['name']}: field layout does not round-trip for this game version")
            continue
        wrong = {k: tree.get(k) for k, v in t["expect"].items() if tree.get(k) != v}
        if wrong:
            log(f"  SKIP {t['name']}: settings differ from the expected ones {wrong}")
            continue
        for k, v in t["set"].items():
            tree[k] = v
        new = encode(tree, node, obj)
        changed = sum(a != b for a, b in zip(raw, new))
        if len(new) != len(raw) or not 0 < changed <= MAX_CHANGED_BYTES:
            log(f"  SKIP {t['name']}: patched object changed size or too many bytes ({changed})")
            continue
        data[start:start + len(raw)] = new
        log(f"  {t['name']}: patched ({changed} bytes, object {hashlib.sha256(raw).hexdigest()[:12]})")
        done += 1
    if done:
        with open(out, "wb") as f:
            f.write(data)
    return done


def apply(files, managed, log=print):
    """Patch every given game file; returns {file: number of targets patched}."""
    result = {}
    for src in files:
        base = os.path.basename(src)
        targets = [t for t in TARGETS if t["file"] == base]
        log(f"{base}:")
        result[base] = patch_file(src, managed, targets, log)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--managed", required=True, help="Dressmaker_Data\\Managed folder")
    a = ap.parse_args()
    for f in a.files:
        if not os.path.isfile(f):
            print(f"FILE NOT FOUND: {f}")
            sys.exit(3)
    res = apply(a.files, a.managed)
    total = sum(res.values())
    print(f"\n{total} of {len(TARGETS)} layout changes applied.")


if __name__ == "__main__":
    main()
