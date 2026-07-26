cd /d %~dp0
cd ../
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%i in (*.toc) do @del "%%i"
del config.yaml
rd /s /q dist
rd /s /q build
rd /s /q app\backend\build
rd /s /q app\backend\dist
rd /s /q venv
rd /s /q app\backend\venv
rd /s /q logs
rd /s /q node_modules
rd /s /q .pnpm-store
rd /s /q app\frontend\build
rd /s /q app\frontend\node_modules
rd /s /q app\frontend\.pnpm-store
pause
