#!/bin/bash
# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause
docker run -it --rm \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -p 3000:3000 \
  -v "$(pwd)/../..:/docker" \
  -w /docker/frontend \
  node:20-bullseye \
  bash -c "corepack enable && corepack prepare pnpm --activate && pnpm install && bash"