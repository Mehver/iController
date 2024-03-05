setlocal enabledelayedexpansion

:: 退回上一级路径
cd ..\..

:: 创建名为“pack-<时间戳>”的文件夹
for /f "delims=" %%a in ('powershell -Command "Get-Date -Format yyyyMMddHHmmss"') do set "timestamp=%%a"
set "folderName=pack-%timestamp%"
mkdir !folderName!

:: 复制文件和文件夹
xcopy .\build .\!folderName!\build /E /I
xcopy .\venv .\!folderName!\venv /E /I
copy config.yaml .\!folderName!\
copy main.py .\!folderName!\
copy .\bin\packaging\init\run.bat .\!folderName!\

echo Files and folders have been copied successfully.
pause
