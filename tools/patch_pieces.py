"""
Dressmaker - translate pattern-piece names stored in resources.assets.

STEP 1 (read-only scan):
    python patch_pieces.py scan "D:\\SteamLibrary\\steamapps\\common\\Dressmaker\\Dressmaker_Data\\resources.assets"
  -> writes pieces_found.txt next to this script. Send that file to Claude.

STEP 2 (after Claude sends pieces_uk.json):
    python patch_pieces.py apply "<ORIGINAL resources.assets>" pieces_uk.json
  -> writes resources.assets.uk next to the input file.

Only strings that exactly match an entry in pieces_uk.json are replaced.
Object names (m_Name) are never touched.
"""
import json
import os
import struct
import sys

import UnityPy

HERE = os.path.dirname(os.path.abspath(__file__))
KEYWORDS = ("bodice", "skirt", "sleeve", "sleev", "collar", "jacket", "bolero", "stays", "dirndl",
            "peplum", "ruffle", "frill", "cup", "strap", "placket", "yoke", "waist", "cuff", "bow",
            "belt", "apron", "undershirt", "underskirt", "overskirt", "undertop", "tier", "trim",
            "panel", "insert", "train", "shoulder", "neck", "ribbon", "flounce", "puff", "wing", "hem",
            "front", "back", "left", "right")
M_NAME_OFFSET = 28  # PPtr(12) + m_Enabled(4 aligned) + PPtr(12)

# ---- rule-based translator for piece names not listed in the JSON ----
N = {'skirt': 'спідниця', 'bodice': 'ліф', 'sleeve': 'рукав', 'sleev': 'рукав', 'collar': 'комір',
     'jacket': 'жакет', 'bolero': 'болеро', 'undershirt': 'нижня сорочка', 'underskirt': 'нижня спідниця',
     'overskirt': 'верхня спідниця', 'undertop': 'нижній топ', 'stays': 'корсаж', 'dirndl': 'дірндль',
     'peplum': 'баска', 'ruffle': 'рюша', 'frill': 'оборка', 'tier': 'ярус', 'trim': 'оздоблення',
     'belt': 'пояс', 'waist': 'талія', 'waistband': 'пояс', 'band': 'смуга', 'strap': 'бретель',
     'ribbon': 'стрічка', 'bow': 'бант', 'placket': 'планка', 'eyelet': 'з люверсами', 'yoke': 'кокетка',
     'cup': 'чашка', 'inner': 'внутр.', 'outer': 'зовн.', 'top': 'верх', 'bottom': 'низ', 'upper': 'верхня',
     'lower': 'нижня', 'middle': 'середина', 'cuff': 'манжета', 'puff': 'буф', 'wing': 'крило',
     'flounce': 'волан', 'bishop': '«єпископ»', 'cap': 'окат', 'shoulder': 'плече', 'pad': 'накладка',
     'neck': 'горловина', 'chest': 'груди', 'cowl': 'драпірування', 'button': 'ґудзиків', 'insert': 'вставка',
     'panel': 'панель', 'drop': 'занижена', 'train': 'шлейф', 'hip': 'стегно', 'apron': 'фартух',
     'attachment': 'кріплення', 'lace': 'мереживо', 'tail': 'хвіст', 'ears': 'вушка', 'central': 'центр',
     'and': 'і'}
D = {'front': 'спереду', 'back': 'ззаду', 'left': 'зліва', 'right': 'справа',
     'f': 'спереду', 'b': 'ззаду', 'l': 'зліва', 'r': 'справа'}
EXCLUDE = {"front lace bodice", "front lace stays"}


def auto_translate(s):
    """Translate a compositional piece name; only if it has a side/number (so design names are skipped)."""
    t = s.strip().lower().replace("waist band", "waistband")
    if t in EXCLUDE:
        return None
    parts, dirs, has_pos = [], [], False
    for w in t.split():
        if w.isdigit():
            if not parts:
                return None
            parts[-1] += " " + str(int(w))
            has_pos = True
            continue
        if w in D:
            if D[w] not in dirs:
                dirs.append(D[w])
            has_pos = True
            continue
        if w not in N:
            return None
        parts.append(N[w])
    if not parts or not has_pos:
        return None
    out = ", ".join(parts)
    if dirs:
        out += " — " + " ".join(dirs)
    out = out.replace(", і, ", " і ").replace("ґудзиків, планка", "планка ґудзиків").replace("занижена, талія", "занижена талія")
    return out[0].upper() + out[1:] + (" " if s.endswith(" ") else "")


def iter_strings(raw):
    """Yield (offset, text) for plausible length-prefixed UTF-8 strings at 4-byte aligned offsets."""
    n = len(raw)
    for i in range(0, n - 4, 4):
        (L,) = struct.unpack_from("<i", raw, i)
        if 2 <= L <= 120 and i + 4 + L <= n:
            b = raw[i + 4:i + 4 + L]
            try:
                s = b.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if s.isprintable() and any(c.isalpha() for c in s):
                yield i, s


def looks_like_piece(s):
    low = s.lower()
    return any(k in low.split() or k in low for k in KEYWORDS) and all(c.isalnum() or c in " -'&" for c in s)


def scan(path):
    env = UnityPy.load(path)
    found = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        for off, s in iter_strings(raw):
            if off == M_NAME_OFFSET:
                continue
            if looks_like_piece(s):
                found[s] = found.get(s, 0) + 1
    out = os.path.join(HERE, "pieces_found.txt")
    with open(out, "w", encoding="utf-8") as f:
        for s in sorted(found):
            f.write(f"{s}\t{found[s]}\n")
    print(f"{len(found)} distinct candidate strings written to:\n{out}")


def rebuild(raw, table):
    """Rebuild object bytes, replacing matching length-prefixed strings; keeps 4-byte alignment."""
    out = bytearray()
    i = 0
    n = len(raw)
    replaced = 0
    while i < n:
        if i % 4 == 0 and i != M_NAME_OFFSET and i + 4 <= n:
            (L,) = struct.unpack_from("<i", raw, i)
            if 2 <= L <= 120 and i + 4 + L <= n:
                try:
                    s = raw[i + 4:i + 4 + L].decode("utf-8")
                except UnicodeDecodeError:
                    s = None
                repl = None
                if s is not None:
                    repl = table.get(s) or auto_translate(s)
                if repl:
                    new = repl.encode("utf-8")
                    out += struct.pack("<i", len(new)) + new
                    out += b"\x00" * ((-len(out)) % 4)
                    end = i + 4 + L
                    i = end + ((-end) % 4)
                    replaced += 1
                    continue
        out.append(raw[i])
        i += 1
    return bytes(out), replaced


def apply(path, json_path):
    with open(json_path, encoding="utf-8") as f:
        table = json.load(f)
    env = UnityPy.load(path)
    total = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        new, n = rebuild(raw, table)
        if n:
            obj.set_raw_data(new)
            total += n
    if not total:
        print("Nothing replaced - is this the ORIGINAL resources.assets?")
        sys.exit(2)
    out = path + ".uk"
    with open(out, "wb") as f:
        f.write(env.file.save())
    print(f"Done: {total} strings replaced. Saved to:\n{out}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "scan":
        scan(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "apply":
        apply(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "pieces_uk.json"))
    else:
        print(__doc__)
