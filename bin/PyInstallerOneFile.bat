cd /d %~dp0
cd ../

for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%i in (*.toc) do @del "%%i"
rd /s /q dist
rd /s /q build
rd /s /q venv
rd /s /q logs

where docker >nul 2>nul
if %errorlevel% neq 0 (
     cd ClientBrowserUI
     npm install
     npm run build
     cd ..
) else (
    docker run -it --rm -v %cd%:/docker -w /docker node:16-bullseye bash -c "cd ClientBrowserUI; npm i; npm run build; exit"
)

python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
pyinstaller iController.spec

pause