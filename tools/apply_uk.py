"""
Dressmaker - Ukrainian translation patcher.

Writes the Ukrainian strings from uk_strings.json straight into the ORIGINAL
English string-tables bundle, using UnityPy (handles Unity 6 bundles correctly).

Setup (once):
    pip install UnityPy

Usage:
    python apply_uk.py "D:\\path\\to\\ORIGINAL\\localization-string-tables-english(en)_assets_all.bundle"

Output: a new file next to the input, ending in  .uk.bundle
Rename it to  localization-string-tables-english(en)_assets_all.bundle  and put it in
    Dressmaker_Data\\StreamingAssets\\aa\\StandaloneWindows64\\
(keep your backup of the original!). The patched catalog.bin must also be in place.
"""
import json
import os
import sys

import UnityPy

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    strings_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "uk_strings.json")
    with open(strings_path, encoding="utf-8") as f:
        tables = json.load(f)

    if not os.path.isfile(src):
        print(f"FILE NOT FOUND:\n{src}\nCheck the path / file name (brackets around 'en' included).")
        sys.exit(3)
    print(f"Input: {src}  ({os.path.getsize(src)} bytes)")

    env = UnityPy.load(src)
    print(f"Objects in bundle: {len(env.objects)}")
    total = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        tree = obj.read_typetree()
        name = tree.get("m_Name")
        print(f"  found MonoBehaviour: {name}")
        if name not in tables or "m_TableData" not in tree:
            continue
        uk = tables[name]
        n = 0
        for entry in tree["m_TableData"]:
            key = str(entry["m_Id"])
            if key in uk:
                entry["m_Localized"] = uk[key]
                n += 1
        obj.save_typetree(tree)
        print(f"{name}: {n} strings replaced")
        total += n

    if total == 0:
        print("Nothing replaced - is this the ORIGINAL English string-tables bundle?")
        sys.exit(2)

    out = src + ".uk.bundle"
    with open(out, "wb") as f:
        f.write(env.file.save(packer="lz4"))
    print(f"\nDone: {total} strings. Saved to:\n{out}")


if __name__ == "__main__":
    main()
