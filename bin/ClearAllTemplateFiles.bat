cd /d %~dp0
cd ../
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
pause
