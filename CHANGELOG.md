# Changelog

## v1.1.0-beta — 2026-11-01
- Shorter item names (930 fabrics, trims, lace, bows and accessories) in the format «Тип, колір», e.g. «Мереживо, айворі», «Подвійна рюша, айворі», «Великий бант, пудровий». The median name is now 1.15× the English width (was 1.47×), and none is wider than the longest English name.
- One colour glossary for all items (260 colours, `docs/glossary.md`), e.g. Ivory → айворі, Dusty Pink → пудровий, Teal → морська хвиля, Blue Jay → волошковий, Royal Blue → електрик. Trims without another type are «Тасьма»; bows no longer repeat the fabric.
- **New, please test:** inventory list names now wrap to two lines and shrink to 13–18 pt instead of being cut off; the cutting-room fabric name shrinks to fit (18–36 pt). New installer step `patch_layout.py` writes 5 bytes from a per-game-build table (`translation/layout_patch.json`, made by `tools/make_layout_table.py`) after checking each object's SHA-256, and skips itself on any mismatch; the installer now also backs up `level2` and `sharedassets2.assets`. If the game misbehaves, run the installer again and choose **2 = Uninstall**.
- `tools/check_widths.py` (run by GitHub Actions on every translation change): fails if an item name is wider than the widest English one or if two different items share a name.

## v1.0.0 — 2026-10-29
- First full release. Same translation as v0.9.1-beta, playtested in-game on the October 2026 patch.
- Installer is now built and published automatically by GitHub Actions when a version tag is pushed.
- Translation fixes and reports: GitHub Issues (label `lqa`).

## v0.9.1-beta — 2026-10-24
- Updated for the October 2026 game patch (new text tables, new catalog).
- 35 new/changed strings translated: new Options sections (Gameplay, Graphics, Audio, Less Animation, Outlines, Bloom…),
  cutting-room tooltips, sketchbook paging tips, camera/mannequin controls, "Reward" label, "Sell As Off-Rack".
- Verified against the patched game files: 5,859 strings applied, 1,671 pattern-piece names patched, file structure intact.

## v0.9-beta — 2026-10
- ~5,800 strings translated: UI, tutorial, fabrics & items, dialogue, newspaper.
- ~600 pattern-piece names in `resources.assets` translated.
- Tools: `apply_uk.py`, `patch_catalog.py`, `patch_pieces.py`, `find_text.py`; one-click `install.bat` / `uninstall.bat`; standalone `DressmakerUA-Installer.exe` built by GitHub Actions.
- Verified on two PCs (Steam release build, Unity 6000.3.4f1).
