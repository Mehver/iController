<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/docs/icon/256.png" width="20%" alt=""/>
    <h1>iController <code>v0.6.6</code></h1>
	<p>English | <a href='https://github.com/Mehver/iController/blob/main/docs/README-cn.md'>简体中文</a></p>
    <span>
        <a href='https://github.com/Mehver/iController/releases/tag/v0.6.6'><img src="https://img.shields.io/badge/Windows%20(x64)-v0.6.6-blue?logo=Windows" alt=""/></a>&nbsp;
        <a href='https://github.com/Mehver/iController/releases/tag/v0.5.1'><img src="https://img.shields.io/badge/MacOS%20(arm64)-v0.5.1-green?logo=Apple" alt=""/></a>&nbsp;
        <a href='https://github.com/Mehver/iController/releases/tag/v0.5.1'><img src="https://img.shields.io/badge/MacOS%20(x64)-v0.5.1-green?logo=Apple" alt=""/></a>
    </span>
</div>

## 1 Description

A host LAN controller software running on `Windows` and `macOS` (read description below) PC, enabling mobile phones to access a web page panel for PC control.

<table>
    <tr>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/docs/A.png" width="390px" alt=""/>
        </td>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/docs/B.png" width="390px" alt=""/>
        </td>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/docs/C.png" width="390px" alt=""/>
        </td>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/docs/D.png" width="390px" alt=""/>
        </td>
    </tr>
</table>

### 1.1 Features

- [x] Touchpad
- [x] Mouse Buttons (Left, Right, Middle)
- [x] Mouse Wheel
- [x] D-Pad
- [x] Keyboard
- [x] Volume Slider

## 2 Usage

### 2.1 Windows

Download portable application from the [Release](https://github.com/Mehver/iController/releases) page.

Currently, the program is CLI interactive. When starting, you can manually provide the port number, and the program will automatically detect to ensure that the port is available and conflict-free. After starting, use the mobile browser to access the LAN IP address and port of the computer.

<img src="https://github.com/Mehver/iController/raw/main/docs/0.png" width="50%" alt="">

### 2.2 macOS

> [!IMPORTANT]
> Due to the introduction of additional features starting from `v0.6.0`, it is difficult to perfectly support macOS through the non-installation method. Therefore, the packaging files for macOS are temporarily not provided, `v0.5.1` is the last stable version that supports macOS.

For `v0.5.1`, you can download from the [Release v0.5.1](https://github.com/Mehver/iController/releases/tag/v0.5.1) page.

Note: For macOS, due to permission issues, the
directly downloaded iController cannot be trusted by the system, the only solution at present is to open the switch
of `Settings > Privacy & Security > Developer Tools > Terminal`.

<img src="https://github.com/Mehver/iController/raw/main/docs/1.jpg" width="50%" alt="">

## 3 Development

### 3.1 Requirements

- [Node.js](https://nodejs.org/en/) v16.20.2
- [Python](https://www.python.org/) v3.10.10

### 3.2 Frontend

All front-end development is carried out in the `./ClientBrowserUI/` directory. The final static ES6 front-end assets are generated using `npm run build`. In both development mode and during packaging, the backend can automatically route requests to the built resource path.

You can set up a Node.js environment on your system and install dependencies using `npm i`. However, the recommended approach is to use the `.bat` or `.sh` scripts provided under `./bin/DevDockerEnv/` in this project to start the official Docker environment and install dependencies with a single command. Scripts whose filenames contain `-p3000` map port 3000, making them convenient for React.js development and debugging.

**Development**

```shell
npm run react
```

**Build**

```shell
npm run build
```

### 3.3 Backend

For the Python environment, since this program is intended to control the mouse in a GUI environment, using containers to isolate the development environment provides limited value. Therefore, it is recommended to use a [Python local virtual environment](https://docs.python.org/3/library/venv.html) to install dependency libraries. It is recommended to use the `.bat` or `.sh` scripts under `./bin/DevPyVenv/` to create the virtual environment and install dependencies into this local virtual environment with a single command.

You can either bind the virtual environment to your IDE or manually activate the virtual environment. For details, see the [official documentation](https://docs.python.org/3/library/venv.html#how-venvs-work). Specifically:

**Windows**

```shell
venv\Scripts\activate
```

**macOS**

```shell
source venv/bin/activate
```

### 3.4 Compile / Package

Recommend use `win-onefile.bat` / `mac-onefile.sh` in `./bin/packaging/` to package the application. **Note that after testing, some Python v3.10.x versions may have mysterious errors. Only Python v3.10.10 is recommended.**

## 4 Built With / Tech Stack

> All dependencies are open-source and licensed under permissive licenses. No copyleft (e.g., GPL, AGPL) components are included.

- Node.js
    - React.js
        - Material UI (https://github.com/mui/material-ui)
        - Prime React (https://github.com/primefaces/primereact)
        - React Color (https://github.com/casesandberg/react-color)
    - Lodash (https://github.com/lodash/lodash)
- Python
    - (≤v0.4.5) ~~Flask (https://github.com/pallets/flask)~~
    - (v0.5.0+) Quart (https://github.com/pallets/quart)
      - Hypercorn (https://github.com/pgjones/hypercorn)
    - PyAutoGUI (https://github.com/asweigart/pyautogui)
    - Pycaw (https://github.com/AndreMiras/pycaw)
    - Psutil (https://github.com/giampaolo/psutil)
    - PyInstaller (https://github.com/pyinstaller/pyinstaller)

## 5 License

This project is released under the BSD 3-Clause License. Code may be reused with proper attribution.

Copyright (c) 2024-Present, Mehver (https://github.com/Mehver). All rights reserved.

All dependencies are open-source and licensed under permissive licenses. No copyleft (e.g., GPL, AGPL) components are included.
