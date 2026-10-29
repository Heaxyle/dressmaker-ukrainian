# Changelog

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
