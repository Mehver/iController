REM 此文件在执行./bin/packaging/win-zipack.bat时会被复制到打包目录下，作为打包后程序的启动文件
REM This file will be copied to the packaging directory when running ./bin/packaging/win-zipack.bat,
REM and it will be used as the startup file for the packaged program.
@echo off
cmd /k "cd /d %~dp0venv\Scripts & activate & cd /d %~dp0 & python main.py"