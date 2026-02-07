cd /d %~dp0
cd ../../

for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%i in (*.toc) do @del "%%i"
del config.yaml
rd /s /q dist
rd /s /q build
rd /s /q backend\build
rd /s /q backend\dist
rd /s /q venv
rd /s /q backend\venv
rd /s /q logs
rd /s /q node_modules
rd /s /q frontend\build
rd /s /q frontend\node_modules

docker run -it --rm -v %cd%:/docker -w /docker node:16-bullseye bash -c "cd frontend; npm i; npm run build; exit"

cd backend

python -m venv venv
call venv\Scripts\activate
pip install -r ./requirements/iControllerGUI.txt
pyinstaller ./pyinstaller/iControllerGUI.spec

pause