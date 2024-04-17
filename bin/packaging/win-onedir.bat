cd /d %~dp0
cd ../../
call venv\Scripts\activate
pyinstaller --noconfirm --onedir --console --icon "#README/icon/256a.ico" --add-data "build;build/" --add-data "modules;modules/" "iController.py"
pause
