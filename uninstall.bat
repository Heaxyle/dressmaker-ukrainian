@echo off
chcp 65001 >nul
echo Restoring original English files... / Відновлення оригінальних файлів...
python "%~dp0tools\install.py" uninstall %*
pause
