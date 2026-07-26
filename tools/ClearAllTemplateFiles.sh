#!/bin/sh
# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause
cd "$(dirname "$0")" || exit 1
cd .. || exit 1
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
rm -rf node_modules
rm -rf .pnpm-store
rm -rf "app/frontend/build"
rm -rf "app/frontend/node_modules"
rm -rf "app/frontend/.pnpm-store"
printf "Press Enter to continue..."
read _
