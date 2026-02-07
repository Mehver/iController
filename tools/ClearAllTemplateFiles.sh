#!/bin/sh
cd "$(dirname "$0")" || exit 1
cd .. || exit 1
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.toc" -exec rm -f {} +
rm -f config.yaml
rm -rf dist
rm -rf build
rm -rf venv
rm -rf "backend/venv"
rm -rf logs
rm -rf node_modules
rm -rf "frontend/build"
rm -rf "frontend/node_modules"
printf "Press Enter to continue..."
read _
