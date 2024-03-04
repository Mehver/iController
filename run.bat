@echo off
cmd /k "cd /d %~dp0venv\Scripts & activate & cd /d %~dp0 & python main.py"