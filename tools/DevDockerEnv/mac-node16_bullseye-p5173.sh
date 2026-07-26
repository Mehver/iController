#!/bin/bash
# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause
docker run -it --rm \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -p 5173:5173 \
  -v "$(pwd)/../..:/docker" \
  -w /docker/app/frontend \
  node:22-bullseye \
  bash -c "corepack enable && corepack prepare pnpm --activate && pnpm install && bash"

read -p "Press Enter to exit..."
