cd /d %~dp0
cd ../

rd /s /q frontend\build
rd /s /q frontend\node_modules

docker run -it --rm -v %cd%:/docker -w /docker node:16-bullseye bash -c "npm install -g npm-check-updates; cd frontend; ncu -u; npm i; npm run build; exit"

pause
