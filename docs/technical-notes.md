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

## Translation approach
- Strings de-duplicated, translated in context, re-inserted by `m_Id`.
- Automated checks: every `{n}` placeholder, smart-string (`{0:list:…}`) and rich-text tag (`<i>`, `<style=…>`, `<size=…>`, `<shake>`…) must match the source.
- ~45 developer/debug strings (`Stub`, `Lorem ipsum`, test quests) intentionally left in English.
