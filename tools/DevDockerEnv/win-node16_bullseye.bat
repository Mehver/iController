docker run -it --rm ^
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 ^
  -v "%cd%\..\..:/docker" ^
  -w /docker/frontend ^
  node:20-bullseye ^
  bash -c "corepack enable && corepack prepare pnpm --activate && pnpm install && bash"