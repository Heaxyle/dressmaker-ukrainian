"""
Dressmaker - let two item-name labels fit longer (Ukrainian) names.
Pure Python, no extra packages: it writes the bytes listed in
translation/layout_patch.json (made by make_layout_table.py for this game build).

  * Inventory list name (sharedassets2.assets): wrap, auto-size 13-18 pt.
  * Cutting room fabric name (level2): auto-size 18-36 pt.

Usage:
    python patch_layout.py "<GAME>\\Dressmaker_Data\\level2" "<GAME>\\Dressmaker_Data\\sharedassets2.assets"

Writes <file>.uk next to each input. Before writing anything it checks, for every
listed object, the SHA-256 of its original bytes and the old value at every offset.
If anything differs (another game build), no file is changed: each .uk is an
unchanged copy and the step reports that it was skipped.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "..", "translation", "layout_patch.json")


def check(data, entry):
    """Return a reason this file's entry does not match, or None."""
    for p in entry["patches"]:
        start, size = p["object_offset"], p["object_size"]
        obj = data[start:start + size]
        if len(obj) != size or hashlib.sha256(obj).hexdigest() != p["object_sha256"]:
            return f"{p['name']}: object bytes differ (other game build)"
        for e in p["edits"]:
            old = bytes.fromhex(e["old"])
            if data[e["offset"]:e["offset"] + len(old)] != old:
                return f"{p['name']}: unexpected value of {e['field']}"
    return None


def apply(files, table_path=TABLE, log=print):
    """Patch all files or none. Returns True if the layout patch was applied."""
    with open(table_path, encoding="utf-8") as f:
        table = json.load(f)["files"]
    datas, reason = {}, None
    for src in files:
        base = os.path.basename(src)
        with open(src, "rb") as f:
            datas[src] = bytearray(f.read())
        if base not in table:
            reason = f"{base}: not in the layout table"
        else:
            reason = check(datas[src], table[base])
        if reason:
            break
    if reason:
        log(f"  Skipped: {reason}. Item names may be cut off; everything else is translated.")
        for src in files:
            shutil.copyfile(src, src + ".uk")
        return False
    for src in files:
        data = datas[src]
        for p in table[os.path.basename(src)]["patches"]:
            for e in p["edits"]:
                new = bytes.fromhex(e["new"])
                data[e["offset"]:e["offset"] + len(new)] = new
            log(f"  {p['name']}")
        with open(src + ".uk", "wb") as f:
            f.write(data)
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for f in sys.argv[1:]:
        if not os.path.isfile(f):
            print(f"FILE NOT FOUND: {f}")
            sys.exit(3)
    ok = apply(sys.argv[1:])
    print("\nLayout patch applied." if ok else "\nLayout patch skipped; files written unchanged.")


if __name__ == "__main__":
    main()
