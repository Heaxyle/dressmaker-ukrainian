# Dressmaker — Ukrainian fan translation / Українізатор

**[English](#english) · [Українська](#українська)**

> ⚠️ Unofficial fan project. Not affiliated with or endorsed by **Cozy Lives** or **Free Lives**.
> Requires a legal Steam copy of *Dressmaker*. **No game files are distributed** — the scripts patch your own copy.
> If the developers ask, or release an official Ukrainian translation, this project will be taken down.

---

## English

Unofficial Ukrainian localization of [Dressmaker](https://store.steampowered.com/app/4019220/Dressmaker/) (PC, Steam).

| | |
|---|---|
| **Translated** | ~5,800 strings: UI, tutorial, fabrics & items (short names: «Тип, колір»), all dialogue, newspaper columns, ~600 pattern-piece names |
| **Translation & tools** | AI-generated (Claude, Anthropic) |
| **Testing, integration & LQA** | Heaxyle, with native-speaker playtesting |
| **Status** | 🧪 **Beta (v1.1.0-beta)** — shorter item names and a new layout fix so they fit; stable release: v1.0.0. Found a mistake? Please [report it](../../issues/new/choose). |
| **Game version tested** | Steam, October 2026 patch (Unity 6000.3.4f1) |

### Known limitations
- Text baked into images (newspaper/flyer art) stays in English.
- Cyrillic uses a fallback sans-serif font (the game's font has no Cyrillic glyphs).
- The translation replaces the **English** language slot — keep the in-game language set to *English*.
- Steam updates or “Verify integrity of game files” revert the patch — just run the installer again.
- Since v1.1.0-beta the installer also adjusts two labels so long item names fit: the inventory list wraps them to two lines (13–18 pt) and the cutting room shrinks them. This layout fix is new; if the game misbehaves, run the installer again and choose **2 = Uninstall**. After a game update the fix is skipped (with a message) until the translation is updated; names are then cut off as in v1.0.0.

### Install (Windows) — easy way, no Python needed
1. Go to [Releases](../../releases) and download **`DressmakerUA-Installer.exe`**.
2. Double-click the exe. That's it — it checks the game is closed, finds the game, backs up the originals to `Dressmaker\uk_backup\` and patches the game.
3. Launch Dressmaker with the in-game language set to **English**.

To uninstall or update, run the exe again: it detects the installed translation and offers **1 = Reinstall/update** or **2 = Uninstall**.
Windows SmartScreen may warn about an unknown publisher (the exe isn't code-signed): click *More info → Run anyway*, or use the Python method below.

### Install (Windows) — with Python
1. Install **Python 3.10+** from [python.org](https://www.python.org/downloads/) — tick **"Add python.exe to PATH"** during setup.
2. Download this repo: green **Code** button → **Download ZIP** (or the latest [Release](../../releases)), and unzip it.
3. **Close the game**, then double-click **`install.bat`**.
   It installs UnityPy, finds your Dressmaker folder, backs up the original files to `Dressmaker\uk_backup\` and patches the game.
4. Launch Dressmaker with the in-game language set to **English**.

**Uninstall:** double-click `uninstall.bat` (or Steam → Properties → Installed Files → Verify integrity).

**After a game update:** just run the installer again — it notices the new game files, backs them up and re-patches.
If the update changed the game's text, some lines may show in English until the translation is updated.

<details><summary>Manual install (advanced)</summary>

From the `tools` folder, run each script on your <b>original</b> files, then replace each original with the new <code>.uk</code> / <code>.uk.bundle</code> file:

```
pip install UnityPy
python apply_uk.py "<GAME>\Dressmaker_Data\StreamingAssets\aa\StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle" ..\translation\uk_strings.json
python patch_catalog.py "<GAME>\Dressmaker_Data\StreamingAssets\aa\catalog.bin"
python patch_pieces.py apply "<GAME>\Dressmaker_Data\resources.assets" ..\translation\pieces_uk.json
python patch_layout.py "<GAME>\Dressmaker_Data\level2" "<GAME>\Dressmaker_Data\sharedassets2.assets"
```
</details>

### Reporting a translation issue
Open an [issue](../../issues/new/choose) using the **Localization bug** template: screenshot, where it appears, current text, suggested fix.

### Credits & license
- Game © Cozy Lives / Free Lives. All game content belongs to its owners.
- Translation text: [CC BY-NC-SA 4.0](LICENSE-TRANSLATION). Tools: [MIT](LICENSE).
- Technical notes: [docs/technical-notes.md](docs/technical-notes.md) · Glossary: [docs/glossary.md](docs/glossary.md)

---

## Українська

Неофіційна українська локалізація гри [Dressmaker](https://store.steampowered.com/app/4019220/Dressmaker/) (ПК, Steam).

| | |
|---|---|
| **Перекладено** | ~5 800 рядків: інтерфейс, навчання, тканини й предмети (короткі назви «Тип, колір»), усі діалоги, газетні колонки, ~600 назв деталей викрійок |
| **Переклад та інструменти** | згенеровано ШІ (Claude, Anthropic) |
| **Тестування, інтеграція та LQA** | Heaxyle, з тестуванням носієм мови |
| **Статус** | 🧪 **Бета (v1.1.0-beta)** — коротші назви предметів і нове виправлення розмітки, щоб вони вміщалися; стабільний реліз — v1.0.0. Знайшли помилку? [Повідомте](../../issues/new/choose). |

### Відомі обмеження
- Текст, намальований на зображеннях (газета, листівки), лишається англійською.
- Кирилиця відображається запасним шрифтом без засічок.
- Переклад замінює **англійську** мову — у грі має бути вибрано *English*.
- Оновлення Steam або «Перевірити цілісність файлів» скидають переклад — просто запустіть інсталятор ще раз.
- Від v1.1.0-beta інсталятор також підлаштовує два написи, щоб довгі назви предметів вміщалися: в інвентарі назва переноситься на два рядки (13–18 pt), у кімнаті крою — зменшується. Це виправлення нове: якщо гра поводиться дивно, запустіть інсталятор ще раз і виберіть **2 = Видалити**. Після оновлення гри виправлення пропускається (з повідомленням), доки переклад не оновлять; тоді назви обрізаються, як у v1.0.0.

### Встановлення (Windows) — простий спосіб, без Python
1. Відкрийте [Releases](../../releases) і завантажте **`DressmakerUA-Installer.exe`**.
2. Двічі клацніть exe — і все. Програма перевірить, що гра закрита, сама знайде гру, зробить резервні копії й встановить переклад.
3. Запустіть гру з мовою **English**.

Щоб видалити або оновити, запустіть exe ще раз: він побачить встановлений переклад і запропонує **1 = Перевстановити** або **2 = Видалити**.
Windows SmartScreen може попередити про невідомого видавця (exe не підписаний): *Докладніше → Все одно запустити*, або скористайтеся способом із Python нижче.

### Встановлення (Windows) — через Python
1. Встановіть **Python 3.10+** з [python.org](https://www.python.org/downloads/) — під час встановлення позначте **"Add python.exe to PATH"**.
2. Завантажте цей репозиторій: зелена кнопка **Code** → **Download ZIP** (або останній [Release](../../releases)) і розпакуйте.
3. **Закрийте гру** й двічі клацніть **`install.bat`**. Скрипт сам знайде гру, зробить резервні копії в `Dressmaker\uk_backup\` і встановить переклад.
4. Запустіть гру з мовою **English**.

**Видалити:** `uninstall.bat` (або Steam → Властивості → Встановлені файли → Перевірити цілісність).

**Після оновлення гри:** просто запустіть інсталятор ще раз — він помітить нові файли гри, збереже їх і встановить переклад заново.

### Повідомити про помилку перекладу
Створіть [issue](../../issues/new/choose) за шаблоном **Localization bug**: скріншот, де трапилось, поточний текст, як має бути.

### Права
Гра © Cozy Lives / Free Lives. Текст перекладу — CC BY-NC-SA 4.0, інструменти — MIT.
