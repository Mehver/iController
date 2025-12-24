docker run -it --rm ^
  -p 3000:3000 ^
  -v "%cd%\..\..:/docker" ^
  -w /docker/ClientBrowserUI ^
  node:16-bullseye ^
  bash -c "npm install && bash"