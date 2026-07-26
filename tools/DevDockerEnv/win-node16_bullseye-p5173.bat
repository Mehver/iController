docker run -it --rm ^
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 ^
  -p 5173:5173 ^
  -v "%cd%\..\..:/docker" ^
  -w /docker/frontend ^
  node:22-bullseye ^
  bash -c "corepack enable && corepack prepare pnpm --activate && pnpm install && bash"

pause
