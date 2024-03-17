#!/bin/bash
cd "$(dirname "$0")"
cd ../../
find . -name "__pycache__" -type d -exec rm -rf {} +
find . \( -name "*.spec" -o -name "*.toc" \) -type f -exec rm {} +
rm -rf build dist
docker run -it --rm -v "$(pwd)":/docker -w /docker node:16-bullseye bash -c "npm i; npm run build; exit"
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
if [ -z "$CI" ]; then
  read -p "Press enter to continue"
fi

