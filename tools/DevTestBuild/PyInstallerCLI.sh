#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

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
rm -rf node_modules
rm -rf .pnpm-store
rm -rf "frontend/build"
rm -rf "frontend/node_modules"
rm -rf "frontend/.pnpm-store"

docker run -it --rm \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -v "$PWD":/docker \
  -w /docker \
  node:20-bullseye \
  bash -c "cd frontend; corepack enable && corepack prepare pnpm --activate; pnpm install; pnpm run build; exit"

cd backend

python3 -m venv venv
source venv/bin/activate
pip install -r ./requirements/iControllerCLI.txt
pyinstaller ./pyinstaller/iControllerCLI.spec
