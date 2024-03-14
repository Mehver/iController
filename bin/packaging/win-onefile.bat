cd /d %~dp0
cd ../../
call venv\Scripts\activate
pyinstaller --noconfirm --onefile --console --icon "#README/icon/256.ico" --add-data "build;build/" "main.py"
pause
