cd /d %~dp0
cd ../

rd /s /q ClientBrowserUI\build
rd /s /q ClientBrowserUI\node_modules

docker run -it --rm -v %cd%:/docker -w /docker node:16-bullseye bash -c "npm install -g npm-check-updates; cd ClientBrowserUI; ncu -u; npm i; npm run build; exit"

pause
