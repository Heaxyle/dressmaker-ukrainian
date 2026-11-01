# Technical notes

## Game
- Unity **6000.3.4f1**, Mono scripting backend.
- Text: **Unity Localization** package, loaded through **Addressables**.
- Bundle: `StreamingAssets/aa/StandaloneWindows64/localization-string-tables-english(en)_assets_all.bundle`
  — StringTables `UI_en` (208), `Tutorial_en` (71), `Content_en` (1930), `Dialogue_en` (3677).
- Catalog: `StreamingAssets/aa/catalog.bin` (binary Addressables catalog).

## Problems found during integration & how they were resolved
| # | Symptom | Evidence | Cause | Fix |
|---|---|---|---|---|
| 1 | Every UI string showed `No translation found for '…' in UI` | screenshot | Whole string table failed to load | investigated further (#2, #3) |
| 2 | — | `Player.log`: `Unable to open archive file` | Bundle re-saved with UABEA is unreadable by Unity 6 | Switched to UnityPy (`apply_uk.py`) |
| 3 | — | catalog inspection | Addressables CRC check rejects modified bundles | `patch_catalog.py` sets bundle CRCs to 0 |
| 4 | Pattern-piece tooltips (e.g. “Bodice Cup Top Right”) still English | in-game screenshot; `find_text.py` → `resources.assets` | Piece names stored in pattern data (no typetrees), not in string tables | `patch_pieces.py`: replaces length-prefixed strings in MonoBehaviour raw data; object names untouched |
| 5 | Edited money reverted on 2nd PC | folder screenshot | Windows hid file extensions; `.lastgood` backup was edited instead of `player.json` | Edit `player.json` with extensions shown |
| 6 | Long item names cut off ("…") in the inventory list, overflowing in the cutting room | TMP survey of all scenes/prefabs with type trees generated from `Managed\*.dll` | Fonts have no Cyrillic: TMP falls back to Liberation Sans (wider); inventory name is fixed 18 pt, one line, 150×42; cutting-room name fixed 36 pt | Shorter names («Тип, колір»), plus `patch_layout.py`: inventory name wraps + auto-sizes 13–18 pt, cutting-room name auto-sizes 18–36 pt |

## Layout patch (`patch_layout.py`)
- Files: `level2` (cutting room) and `sharedassets2.assets` (inventory list item prefab). They carry no type trees, so the TMP field layout is generated at install time from the game's `Managed` DLLs (`TypeTreeGeneratorAPI`).
- A target is found by its object path and patched only if its current settings are the expected originals, the unmodified object re-encodes to its exact original bytes, and the patched object keeps its length and changes at most 16 bytes (in practice 4 and 1). New bytes are written in place; nothing else is re-serialized.
- Otherwise the target is skipped with a message and the file is installed unchanged; the text translation never depends on it.
- The game code never sets auto-size, wrapping or overflow at runtime, so the stored settings are what players see.

## Translation approach
- Strings de-duplicated, translated in context, re-inserted by `m_Id`.
- Automated checks: every `{n}` placeholder, smart-string (`{0:list:…}`) and rich-text tag (`<i>`, `<style=…>`, `<size=…>`, `<shake>`…) must match the source.
- ~45 developer/debug strings (`Stub`, `Lorem ipsum`, test quests) intentionally left in English.
