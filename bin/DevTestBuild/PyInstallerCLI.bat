cd /d %~dp0
cd ../../

for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%i in (*.toc) do @del "%%i"
del config.yaml
rd /s /q dist
rd /s /q build
rd /s /q venv
rd /s /q logs
rd /s /q node_modules
rd /s /q ClientBrowserUI\build
rd /s /q ClientBrowserUI\node_modules

docker run -it --rm -v %cd%:/docker -w /docker node:16-bullseye bash -c "cd ClientBrowserUI; npm i; npm run build; exit"

python -m venv venv
call venv\Scripts\activate
pip install -r ./requirements/iControllerCLI.txt
pyinstaller ./pyinstaller/iControllerCLI.spec

pause