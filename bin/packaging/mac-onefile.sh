#!/bin/bash
cd "$(dirname "$0")"
cd ../../
source venv/bin/activate
pyinstaller --noconfirm --onefile --console --icon "#README/icon/256a.icns" --add-data "build:build/" --add-data "modules:modules/"  "app.py"
if [ -z "$CI" ]; then
  read -p "Press enter to continue"
fi
