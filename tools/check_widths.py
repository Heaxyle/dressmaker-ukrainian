"""
Dressmaker - check that Ukrainian item names are not much wider than the English ones.

The English text is game content and is not kept in this repo, so
translation/item_widths.json stores only the rendered width of each English item
name (pixels, EB Garamond at 32 px) and a short hash of it, keyed by its Content_en id.

Usage:
    python check_widths.py
        Measure every Ukrainian item name in translation/uk_strings.json against
        the stored English widths. Exit code 1 if any name is wider than the
        widest English item name (the UI already has to fit that one), or if two
        different items share one Ukrainian name (rows with the same English
        name are the same item and may share it).
        Names wider than 1.3x their English name are listed as warnings.

    python check_widths.py measure-en "<GAME>\\Dressmaker_Data\\StreamingAssets\\aa\\StandaloneWindows64\\localization-string-tables-english(en)_assets_all.bundle"
        Re-measure the English widths from an ORIGINAL bundle (after a game update).
        Ids already in item_widths.json are kept; add new item ids to that file by hand.

Options:
    --font PATH   TTF to measure with (default: tools/fonts/EBGaramond.ttf)
    --ratio X     warning threshold (default 1.3)

Setup (once):
    pip install pillow
    Download EB Garamond (OFL) into tools/fonts/EBGaramond.ttf:
    https://github.com/google/fonts/raw/main/ofl/ebgaramond/EBGaramond%5Bwght%5D.ttf
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
WIDTHS = os.path.join(ROOT, "translation", "item_widths.json")
STRINGS = os.path.join(ROOT, "translation", "uk_strings.json")
SIZE = 32


def load_font(path):
    from PIL import ImageFont
    if not os.path.isfile(path):
        print(f"Font not found: {path}\nDownload EB Garamond, see the top of this script.")
        sys.exit(2)
    return ImageFont.truetype(path, SIZE)


def en_hash(text):
    """Short hash of an English name: tells rows of the same item apart from different items."""
    return hashlib.sha1(text.strip().lower().encode("utf-8")).hexdigest()[:10]


def duplicates(data, uk):
    """Ukrainian names used by items whose English names differ."""
    by_name = {}
    for k, group in data.get("groups", {}).items():
        if k in uk:
            by_name.setdefault(uk[k].strip(), {}).setdefault(group, []).append(k)
    return {name: g for name, g in by_name.items() if len(g) > 1}


def measure_en(bundle, font):
    import UnityPy
    data = json.load(open(WIDTHS, encoding="utf-8"))
    env = UnityPy.load(bundle)
    en = None
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            if tree.get("m_Name") == "Content_en":
                en = {str(e["m_Id"]): e["m_Localized"] for e in tree["m_TableData"]}
    if en is None:
        print("Content_en not found - is this the ORIGINAL English string-tables bundle?")
        sys.exit(2)
    missing = [k for k in data["items"] if k not in en]
    data.setdefault("groups", {})
    for k in data["items"]:
        if k in en:
            data["items"][k] = round(font.getlength(en[k].strip()))
            data["groups"][k] = en_hash(en[k])
    data["limit"] = max(data["items"].values())
    with open(WIDTHS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(data['items']) - len(missing)} English widths measured, limit {data['limit']} px.")
    if missing:
        print(f"{len(missing)} ids are no longer in the game: {', '.join(missing)}")


def check(font, ratio):
    data = json.load(open(WIDTHS, encoding="utf-8"))
    uk = json.load(open(STRINGS, encoding="utf-8"))["Content_en"]
    limit = data["limit"]
    over, warn = [], []
    for k, w_en in data["items"].items():
        if k not in uk:
            continue
        w_uk = round(font.getlength(uk[k].strip()))
        if w_uk > limit:
            over.append((w_uk, k, uk[k]))
        elif w_uk > ratio * w_en:
            warn.append((w_uk / w_en, w_uk, k, uk[k]))
    print(f"{len(data['items'])} item names checked; limit {limit} px (widest English name).")
    if warn:
        print(f"\n{len(warn)} names wider than {ratio}x English (warning only). Widest 20:")
        for r, w, k, s in sorted(warn, key=lambda x: -x[1])[:20]:
            print(f"  {r:.2f}x  {w:4d} px  {k}  {s}")
    dup = duplicates(data, uk)
    if over:
        print(f"\nFAIL: {len(over)} names wider than {limit} px:")
        for w, k, s in sorted(over, reverse=True):
            print(f"  {w:4d} px  {k}  {s}")
    if dup:
        print(f"\nFAIL: {len(dup)} Ukrainian names are shared by different items:")
        for name, groups in sorted(dup.items()):
            print(f"  {name}: ids {', '.join(sorted(sum(groups.values(), [])))}")
    if over or dup:
        sys.exit(1)
    print("\nOK: no name is wider than the widest English name, and no two items share a name.")


def main():
    ap = argparse.ArgumentParser(description="Check Ukrainian item name widths.")
    ap.add_argument("command", nargs="?", default="check", choices=["check", "measure-en"])
    ap.add_argument("bundle", nargs="?")
    ap.add_argument("--font", default=os.path.join(HERE, "fonts", "EBGaramond.ttf"))
    ap.add_argument("--ratio", type=float, default=1.3)
    a = ap.parse_args()
    font = load_font(a.font)
    if a.command == "measure-en":
        if not a.bundle:
            print(__doc__)
            sys.exit(1)
        measure_en(a.bundle, font)
    else:
        check(font, a.ratio)


if __name__ == "__main__":
    main()
