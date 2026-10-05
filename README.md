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
| **Translated** | ~5,800 strings: UI, tutorial, fabrics & items, all dialogue, newspaper columns, ~600 pattern-piece names |
| **Translation & tools** | AI-generated (Claude, Anthropic) |
| **Testing, integration & LQA** | Heaxyle, with native-speaker playtesting |
| **Status** | 🧪 **Beta (v0.9)** — complete translation, LQA playtesting in progress. Expect some inaccuracies; please [report them](../../issues/new/choose). |
| **Game version tested** | Steam release, Unity 6000.3.4f1 (Sept 2026) |

### Known limitations
- Text baked into images (newspaper/flyer art) stays in English.
- Cyrillic uses a fallback sans-serif font (the game's font has no Cyrillic glyphs).
- The translation replaces the **English** language slot — keep the in-game language set to *English*.
- Steam updates or “Verify integrity of game files” revert the patch — just run the installer again.

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
| **Перекладено** | ~5 800 рядків: інтерфейс, навчання, тканини й предмети, усі діалоги, газетні колонки, ~600 назв деталей викрійок |
| **Переклад та інструменти** | згенеровано ШІ (Claude, Anthropic) |
| **Тестування, інтеграція та LQA** | Heaxyle, з тестуванням носієм мови |
| **Статус** | 🧪 **Бета (v0.9)** — переклад повний, триває перевірка якості під час гри. Можливі неточності — [повідомляйте](../../issues/new/choose). |

### Відомі обмеження
- Текст, намальований на зображеннях (газета, листівки), лишається англійською.
- Кирилиця відображається запасним шрифтом без засічок.
- Переклад замінює **англійську** мову — у грі має бути вибрано *English*.
- Оновлення Steam або «Перевірити цілісність файлів» скидають переклад — просто запустіть інсталятор ще раз.

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
