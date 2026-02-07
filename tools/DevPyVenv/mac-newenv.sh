#!/bin/bash

cd "$(dirname "$0")"
cd ../../ || exit 1

find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.toc" -exec rm -f {} +
rm -f config.yaml
rm -rf dist
rm -rf build
rm -rf "backend/build"
rm -rf "backend/dist"
rm -rf venv
rm -rf "backend/venv"
rm -rf logs

cd backend || exit 1

python3 -m venv venv
source venv/bin/activate
pip install -r ./requirements/iControllerGUI.txt
echo "Virtual environment has been created and activated."
read -p "Press any key to continue... " -n1 -s
echo
