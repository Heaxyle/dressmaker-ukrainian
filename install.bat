@echo off
chcp 65001 >nul
echo ============================================
echo  Dressmaker - Ukrainian translation installer
echo  Українізатор Dressmaker
echo ============================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^), then run this again.
  echo Python не знайдено. Встановіть його з python.org ^(позначте "Add python.exe to PATH"^) і запустіть ще раз.
  pause
  exit /b 1
)
echo Close the game before continuing. / Закрийте гру перед продовженням.
pause
python -m pip install --quiet --upgrade UnityPy TypeTreeGeneratorAPI
python "%~dp0tools\install.py" %*
pause
