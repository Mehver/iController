docker run -it --rm ^
  -v "%cd%\..\..:/docker" ^
  -w /docker/frontend ^
  node:16-bullseye ^
  bash -c "npm install && bash"