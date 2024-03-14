#!/bin/bash
cd "$(dirname "$0")"
cd ../../
source venv/bin/activate
pyinstaller --noconfirm --onefile --console --icon="#README/icon/256.icns" --add-data "build:build/" "main.py"
