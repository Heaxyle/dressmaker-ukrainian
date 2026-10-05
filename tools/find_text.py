"""
Dressmaker - find where a piece of English text is stored (v2, raw search).

Usage (from the folder with this script):
    python find_text.py "D:\\SteamLibrary\\steamapps\\common\\Dressmaker\\Dressmaker_Data" "Cup Top Right"

Searches EVERY file under the game's data folder:
  - raw bytes of every file (UTF-8 and UTF-16), incl. Managed\\*.dll code
  - inside every Unity asset/bundle, the raw data of every object
    (works even when the game has no type information)
Read-only: it does not change any files. Paste the output to Claude.
"""
import os
import sys

import UnityPy


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    root, needle = sys.argv[1], sys.argv[2]
    pats = {
        "utf8": needle.encode("utf-8"),
        "utf16": needle.encode("utf-16-le"),
    }
    hits = 0
    for dirpath, _, files in os.walk(root):
        for fn in files:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            try:
                data = open(full, "rb").read()
            except Exception:
                continue
            # 1) raw file search
            for enc, p in pats.items():
                n = data.count(p)
                if n:
                    hits += n
                    print(f"[raw {enc}] {rel}  x{n}")
            # 2) search inside Unity objects (handles compressed bundles)
            if not (data[:7] == b"UnityFS" or fn.endswith(".assets") or fn.startswith("level")
                    or fn == "globalgamemanagers"):
                continue
            try:
                env = UnityPy.load(full)
            except Exception:
                continue
            for obj in env.objects:
                try:
                    raw = obj.get_raw_data()
                except Exception:
                    continue
                for enc, p in pats.items():
                    if p in raw:
                        hits += 1
                        name = ""
                        try:
                            name = getattr(obj.peek_name(), "__str__", lambda: "")() if hasattr(obj, "peek_name") else ""
                        except Exception:
                            pass
                        print(f"[object {enc}] {rel} | type {obj.type.name} | pathID {obj.path_id} | {name}")
    print(f"\n{hits} match(es) for {needle!r}")


if __name__ == "__main__":
    main()
