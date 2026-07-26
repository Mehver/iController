cd /d %~dp0
cd ../

rd /s /q app\frontend\build
rd /s /q app\frontend\node_modules

docker run -it --rm ^
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 ^
  -v "%cd%:/docker" ^
  -w /docker ^
  node:22-bullseye sh -c "corepack enable && corepack prepare pnpm --activate && cd app/frontend && npx -y npm-check-updates -u && pnpm install && pnpm run build"

pause
