cd /d %~dp0
cd ../../

find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.toc" -exec rm -f {} +
rm -f config.yaml
rm -rf dist
rm -rf build
rm -rf "app/backend/build"
rm -rf "app/backend/dist"
rm -rf venv
rm -rf "app/backend/venv"
rm -rf logs

cd app/backend

python -m venv venv
call venv\Scripts\activate
pip install -r ./requirements/iControllerGUI.txt

pause