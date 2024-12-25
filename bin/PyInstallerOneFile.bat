cd /d %~dp0
cd ../
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%i in (*.toc) do @del "%%i"
rd /s /q dist
rd /s /q build
docker run -it --rm -v %cd%:/docker -w /docker node:16-bullseye bash -c "npm i; npm run build; exit"
rd /s /q /venv
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --console --icon "#README/icon/256a.ico" --add-data "build;build/" --add-data "modules;modules/" "iController.py"
pause
