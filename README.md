<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/%23README/icon/256.png" width="20%"/>
    <h1>iController <code>v0.2.1</code></h1>
    </tr>
	<p>English | <a href='https://github.com/Mehver/iController/blob/main/%23README/README-cn.md'>简体中文</a></p>
</div>

## 1 Description

A simple server running on a `Windows`/`macOS` host, which allows mobile phones on the same local area network to
control it as touchpad and keyboard through a web page after connecting.

一个在 `Windows`/`macOS` 主机上运行的简易服务器，同一局域网下的手机连接后可以通过网页实现触摸板和键盘的操作。

### 1.1 Features

- [x] Touchpad
- [x] Mouse Buttons (Left, Right, Middle)
- [x] D-Pad
- [ ] Keyboard
- [ ] Mouse Wheel

*Some features are not completed yet, and will be added in the future.*

### 1.2 Release Note

**v0.2.1 (pre)**

- New Features
  - Manually Input Port Number
- Code
  - Optimized React Component Structure
  - Optimized Python Code Structure

## 2 Usage

### 2.1 Download

Download portable application from the [Release](https://github.com/Mehver/iController/releases) page.

After starting, the phone can access the corresponding address according to the prompt. Please ensure that there is no
problem with the network connection between the phone and the computer. If there is a problem, please debug the firewall
and other settings by yourself. IOS users are recommended to use the "Add to Home Screen" function of Safari.

<img src="https://github.com/Mehver/iController/raw/main/%23README/0.png" width="50%">

***Note: For `macOS`, due to permission issues, the
directly downloaded iController cannot be trusted by the system, the only solution at present is to open the switch
of `Settings > Privacy & Security > Developer Tools > Terminal`.**

<img src="https://github.com/Mehver/iController/raw/main/%23README/1.jpg" width="50%">

### 2.2 Capability

Currently, only `Windows 10 (2024.2)`/`macOS (13.3)` and `IOS 17` under `Safari` browser have been tested, and other
environments have not been tested.

## 3 Development

### 3.1 Requirements

- [Node.js](https://nodejs.org/en/) v16.20.2
- [Python](https://www.python.org/) v3.10.10

### 3.2 Frontend

**Development**

```shell
npm run react
```

**Compile**

```shell
npm run build
```

### 3.3 Backend

**Windows**

For Python environment, recommend using `./bin/dev-pyvenv/newenv.bat` to create a new virtual environment. Then run:

```shell
venv\Scripts\activate
```

to enter the virtual environment. Or add the virtual environment to your IDE.

**macOS**

For Python environment, recommend using `./bin/dev-pyvenv/newenv.sh` to create a new virtual environment. Then run:

```shell
source venv/bin/activate
```

to enter the virtual environment. Or add the virtual environment to your IDE.

### 3.4 Compile / Package

Directly run `auto-py-to-exe` or use `win-onefile.bat` / `mac-onefile.sh` in `./bin/packaging/` to package the application. Note that after testing, some Python v3.10.x versions may have
mysterious errors. Only Python v3.10.10 is recommended.


## 4 Built With / Tech Stack

- Node.js
    - React.js
        - Material UI (https://github.com/mui/material-ui)
        - Ant Design (https://github.com/ant-design/ant-design)
- Python
    - Flask (https://flask.palletsprojects.com/en/3.0.x/)
    - PyAutoGUI (https://pyautogui.readthedocs.io/en/latest/)
    - PyInstaller (https://www.pyinstaller.org/)
    - Auto-PY-To-EXE (https://github.com/brentvollebregt/auto-py-to-exe)

## 5 Similar Projects

- [Trackpad++](https://github.com/pg07codes/trackpadpp)
    - Author: [pg07codes](https://github.com/pg07codes)
    - Language: `JavaScript`
    - License: `MIT`
    - Description: Trackpad++ allows controlling device's cursor using your mobile phone as a touchpad.
    - Note: This project does similar things, but using Robot.js instead of PyAutoGUI. Features such as a keyboard are missing. And it's not been
      updated for a long time. So I decided to make a new one.
- [AndroidTrackpad](https://github.com/teamclouday/AndroidTrackpad)
    - Author: [teamclouday](https://github.com/teamclouday)
    - Language: `C++`, `Java`
    - License: `MIT`
    - Description: Use your android phone as trackpad on Windows or Linux systems.
    - Note: This project is for Android only, and it's not been updated for a long time. The way it works is a bit
      different, it's not using B/S but C/S architecture, which can be a faster but less flexible.

Compare to these projects, iController is designed with PyAutoGUI, which means it can do more things than just
controlling the cursor. But its weakness is that I didn't pay much time on cross-platform support, and it's more laggy
than C/S architecture, feels like a remote desktop control.

## 6 License

MPL 2.0

Copyright © 2024-PRESENT GitHub@Mehver/iController , All Rights Reserved.
