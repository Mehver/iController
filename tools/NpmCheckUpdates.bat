cd /d %~dp0
cd ../

rd /s /q frontend\build
rd /s /q frontend\node_modules

docker run -it --rm ^
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 ^
  -v "%cd%:/docker" ^
  -w /docker ^
  node:20-bullseye sh -c "corepack enable && corepack prepare pnpm --activate && cd frontend && npx -y npm-check-updates -u && pnpm install && pnpm run build"

pause
