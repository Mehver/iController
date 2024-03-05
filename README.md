<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/%23README/icon/256.png" width="20%"/>
    <h1>iController <code>v0.1.2</code></h1>
    </tr>
</div>

## 1 Description

A simple server running on a Windows host, which allows mobile phones on the same local area network to control it as touchpad and keyboard through a web page after connecting.

一个在Windows主机上运行的简易服务器，同一局域网下的手机连接后可以通过网页实现触摸板和键盘的操作。

### 1.1 Features

- [x] Touchpad
- [x] Mouse Buttons (Left, Right, Middle)
- [x] D-Pad
- [ ] Keyboard
- [ ] Mouse Wheel
- [ ] Double Click for Touchpad

*Some features are not completed yet, and will be added in the future.*

## 2 Usage

### 2.1 Download

Download from the [Release](https://github.com/Mehver/iController/releases) page. Currently only provide the `iController-vX.X.X-Portable-Win_x64.zip
` zip file, unzip and start with `run.bat`, no dependencies. After starting, the phone can access the corresponding address according to the prompt. Please ensure that there is no problem with the network connection between the phone and the computer. If there is a problem, please debug the firewall and other settings by yourself. IOS users are recommended to use the "Add to Home Screen" function of Safari.

在 [Release](https://github.com/Mehver/iController/releases) 页面下载。目前只提供下载 `iController-vX.X.X-Portable-Win_x64.zip
` 压缩包，解压后通过 `run.bat` 启动，不依赖任何环境。启动后手机根据提示访问对应地址即可。请确保手机与电脑的网络连接不存在问题，如有问题请自行调试防火墙等设置。IOS用户推荐使用Safari的”添加到主屏幕“功能。

### 2.2 Capability

Currently, only `Windows 10 (2024.2)` and `IOS 17` under `Safari` browser have been tested, and other environments have not been tested.

目前仅测试了 `Windows 10 (2024.2)` 与 `IOS 17` 下的 `Safari` 浏览器，其他环境未测试。

## 3 Development

### 3.1 Requirements

- [Node.js](https://nodejs.org/en/) v16.20.2
- [Python](https://www.python.org/) v3.10.0

### 3.2 Frontend Development

**Development**

```shell
npm run react
```

**Compile**

```shell
npm run build
```

### 3.3 Backend Development

**Windows**

For Python environment, recommend using `./bin/py-newenv.bat` to create a new virtual environment. Then run:

```shell
venv\Scripts\activate
```

to enter the virtual environment.

### 3.4 Compile / Package

**Windows**

Make sure you compiled the frontend first (see 3.2), then run `./bin/pack-win.bat` to package the application. It will generate a `pack-<timestamp>` directory in repository root, which contains the application. You can use `run.bat` to start the application.

## 4 Built With / Tech Stack

- Node.js
  - React.js
    - Material UI (https://github.com/mui/material-ui)
    - Ant Design (https://github.com/ant-design/ant-design)
- Python
  - Flask (https://flask.palletsprojects.com/en/3.0.x/)
  - PyAutoGUI (https://pyautogui.readthedocs.io/en/latest/)

## 5 Similar Projects

- [Trackpad++](https://github.com/pg07codes/trackpadpp)
  - Author: [pg07codes](https://github.com/pg07codes)
  - Language: `JavaScript`
  - License: `MIT`
  - Description: Trackpad++ allows controlling device's cursor using your mobile phone as a touchpad.
  - Note: This project does similar things, but without PyAutoGUI, it can only do limited things. And it's not been updated for a long time. So I decided to make a new one.
- [AndroidTrackpad](https://github.com/teamclouday/AndroidTrackpad)
  - Author: [teamclouday](https://github.com/teamclouday)
  - Language: `C++`, `Java`
  - License: `MIT`
  - Description: Use your android phone as trackpad on Windows or Linux systems.
  - Note: This project is for Android only, and it's not been updated for a long time. The way it works is a bit different, it's not using B/S but C/S architecture, which can be a faster but less flexible.

Compare to these projects, iController is designed with PyAutoGUI, which means it can do more things than just controlling the cursor. But its weakness is that I didn't pay much time on cross-platform support, and it's more laggy than C/S architecture, feels like a remote desktop control.

## 6 License

MPL 2.0

Copyright © 2024-PRESENT GitHub@Mehver/iController , All Rights Reserved.
