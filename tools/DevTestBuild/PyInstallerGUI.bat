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
rd /s /q .pnpm-store
rd /s /q frontend\build
rd /s /q frontend\node_modules
rd /s /q frontend\.pnpm-store

docker run -it --rm -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 -v %cd%:/docker -w /docker node:20-bullseye bash -c "cd frontend; corepack enable && corepack prepare pnpm --activate; pnpm install; pnpm run build; exit"

cd backend

python -m venv venv
call venv\Scripts\activate
pip install -r ./requirements/iControllerGUI.txt
pyinstaller ./pyinstaller/iControllerGUI.spec

pause