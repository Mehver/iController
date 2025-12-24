docker run -it --rm ^
  -v "%cd%\..\..:/docker" ^
  -w /docker/ClientBrowserUI ^
  node:16-bullseye ^
  bash -c "npm install && bash"