#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.toc" -delete
rm -f config.yaml
rm -rf dist
rm -rf build
rm -rf venv
rm -rf logs
rm -rf node_modules
rm -rf frontend/build
rm -rf frontend/node_modules

docker run -it --rm \
  -v "$PWD":/docker \
  -w /docker \
  node:16-bullseye \
  bash -c "cd frontend; npm i; npm run build; exit"

cd backend

python3 -m venv venv
source venv/bin/activate
pip install -r ./requirements/iControllerGUI.txt
pyinstaller ./pyinstaller/iControllerGUI.spec
