"""
Dressmaker Ukrainian translation - one-step installer / uninstaller.

    python install.py              -> install (finds the game automatically, or asks)
    python install.py uninstall    -> restore the original English files
    python install.py "D:\\SteamLibrary\\steamapps\\common\\Dressmaker"   -> install to a given folder

What it does:
  1. Backs up the 3 original game files to  <game>\\uk_backup\\  (only the first time)
  2. Always patches FROM those backups, so re-running is safe
  3. Replaces the game files with the patched versions
"""
import os
import re
import shutil
import sys

FROZEN = getattr(sys, "frozen", False)          # True when running as the standalone .exe
HERE = os.path.dirname(os.path.abspath(__file__))
if FROZEN:
    TRANSLATION = os.path.join(sys._MEIPASS, "translation")
else:
    TRANSLATION = os.path.join(HERE, "..", "translation")
    sys.path.insert(0, HERE)

import apply_uk        # noqa: E402
import patch_catalog   # noqa: E402
import patch_pieces    # noqa: E402
FILES = {
    "bundle": os.path.join("Dressmaker_Data", "StreamingAssets", "aa", "StandaloneWindows64",
                           "localization-string-tables-english(en)_assets_all.bundle"),
    "catalog": os.path.join("Dressmaker_Data", "StreamingAssets", "aa", "catalog.bin"),
    "assets": os.path.join("Dressmaker_Data", "resources.assets"),
}


def steam_libraries():
    roots = [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"]
    libs = []
    for root in roots:
        vdf = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if os.path.isfile(vdf):
            libs.append(root)
            text = open(vdf, encoding="utf-8", errors="ignore").read()
            libs += [p.replace("\\\\", "\\") for p in re.findall(r'"path"\s+"([^"]+)"', text)]
    return list(dict.fromkeys(libs))


def find_game():
    for lib in steam_libraries():
        cand = os.path.join(lib, "steamapps", "common", "Dressmaker")
        if os.path.isfile(os.path.join(cand, FILES["catalog"])):
            return cand
    return None


def ask_game():
    game = find_game()
    if game:
        print(f"Found Dressmaker: {game}")
        return game
    print("Could not find Dressmaker automatically.")
    print("In Steam: right-click Dressmaker > Manage > Browse local files, copy the folder path and paste it here.")
    return input("Game folder: ").strip().strip('"')


def run(name, func, *args):
    """Run one patch step in-process; stop safely if it fails."""
    old_argv = sys.argv
    try:
        sys.argv = [name, *args]
        func()
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"\nERROR in step {name}. Nothing was replaced. Your game is unchanged.")
            finish(1)
    except Exception as e:  # noqa: BLE001
        print(f"\nERROR in step {name}: {e}\nNothing was replaced. Your game is unchanged.")
        finish(1)
    finally:
        sys.argv = old_argv


def finish(code=0):
    if FROZEN:
        input("\nPress Enter to close... / Натисніть Enter, щоб закрити...")
    sys.exit(code)


def file_hash(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def install(game):
    for key, rel in FILES.items():
        if not os.path.isfile(os.path.join(game, rel)):
            print(f"Missing game file: {rel}\nIs this the right folder?")
            finish(1)
    backup = os.path.join(game, "uk_backup")
    os.makedirs(backup, exist_ok=True)
    state = os.path.join(backup, "installed.txt")
    installed = {}
    if os.path.isfile(state):
        for line in open(state, encoding="utf-8"):
            k, _, v = line.strip().partition("=")
            installed[k] = v
    for key, rel in FILES.items():
        cur = os.path.join(game, rel)
        dst = os.path.join(backup, os.path.basename(rel))
        # back up if no backup yet, or if the game file changed since we installed
        # (= Steam update / verify restored fresh originals)
        if not os.path.exists(dst) or (key in installed and file_hash(cur) != installed[key]):
            shutil.copy2(cur, dst)
            print(f"Backed up {os.path.basename(rel)}")
    b = {k: os.path.join(backup, os.path.basename(v)) for k, v in FILES.items()}

    print("\n[1/3] Translating text tables...")
    run("apply_uk", apply_uk.main, b["bundle"], os.path.join(TRANSLATION, "uk_strings.json"))
    print("\n[2/3] Patching catalog...")
    run("patch_catalog", patch_catalog.main, b["catalog"])
    print("\n[3/3] Translating pattern-piece names...")
    run("patch_pieces", lambda: patch_pieces.apply(sys.argv[1], sys.argv[2]),
        b["assets"], os.path.join(TRANSLATION, "pieces_uk.json"))

    outputs = {"bundle": b["bundle"] + ".uk.bundle", "catalog": b["catalog"] + ".uk", "assets": b["assets"] + ".uk"}
    for key, rel in FILES.items():
        shutil.move(outputs[key], os.path.join(game, rel))
    with open(state, "w", encoding="utf-8") as f:
        for key, rel in FILES.items():
            f.write(f"{key}={file_hash(os.path.join(game, rel))}\n")
    print("\nDONE! Launch Dressmaker with language = English. / ГОТОВО! Запустіть гру з мовою English.")


def uninstall(game):
    backup = os.path.join(game, "uk_backup")
    if not os.path.isdir(backup):
        print("No backup found - use Steam > Properties > Installed Files > Verify integrity instead.")
        finish(1)
    for key, rel in FILES.items():
        src = os.path.join(backup, os.path.basename(rel))
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(game, rel))
    shutil.rmtree(backup, ignore_errors=True)
    print("Original English files restored. / Оригінальні файли відновлено.")


def game_running():
    """True if Dressmaker.exe is running (Windows only)."""
    if os.name != "nt":
        return False
    try:
        import subprocess
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Dressmaker.exe"],
                             capture_output=True, text=True).stdout
        return "Dressmaker.exe" in out
    except Exception:  # noqa: BLE001
        return False


def wait_for_game_closed():
    while game_running():
        input("Dressmaker is running - close the game, then press Enter.\n"
              "Гра запущена - закрийте її й натисніть Enter.")


if __name__ == "__main__":
    args = sys.argv[1:]
    print("Dressmaker — Ukrainian translation / Українізатор\n")
    if args and args[0].lower() == "uninstall":
        game = args[1] if len(args) > 1 else ask_game()
        wait_for_game_closed()
        uninstall(game)
    else:
        game = args[0] if args else ask_game()
        wait_for_game_closed()
        already = os.path.isdir(os.path.join(game, "uk_backup"))
        if already and not args:
            print("The translation is already installed. / Переклад уже встановлено.")
            print("  1 = Reinstall / update   (Перевстановити / оновити)")
            print("  2 = Uninstall, restore English   (Видалити, повернути англійську)")
            if input("Choose 1 or 2 / Виберіть 1 або 2: ").strip() == "2":
                uninstall(game)
                finish(0)
        install(game)
    finish(0)
