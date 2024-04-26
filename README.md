<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/%23README/icon/256.png" width="20%" alt=""/>
    <h1>iController <code>v0.6.2</code></h1>
	<p>English | <a href='https://github.com/Mehver/iController/blob/main/%23README/README-cn.md'>简体中文</a></p>
    <span>
        <a href='https://github.com/Mehver/iController/releases/tag/v0.6.2'><img src="https://img.shields.io/badge/Windows%20(x64)-v0.6.2-blue?logo=Windows" alt=""/></a>&nbsp;
        <a href='https://github.com/Mehver/iController/releases/tag/v0.5.1'><img src="https://img.shields.io/badge/MacOS%20(arm64)-v0.5.1-green?logo=Apple" alt=""/></a>&nbsp;
        <a href='https://github.com/Mehver/iController/releases/tag/v0.5.1'><img src="https://img.shields.io/badge/MacOS%20(x64)-v0.5.1-green?logo=Apple" alt=""/></a>
    </span>
</div>

## 1 Description

A host LAN controller software running on `Windows` and `macOS` (read description below) PC, enabling mobile phones to access a web page panel for PC control.

<table>
    <tr>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/%23README/A.png" width="390px" alt=""/>
        </td>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/%23README/B.png" width="390px" alt=""/>
        </td>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/%23README/C.png" width="390px" alt=""/>
        </td>
        <td>
            <img src="https://github.com/Mehver/iController/raw/main/%23README/D.png" width="390px" alt=""/>
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

<img src="https://github.com/Mehver/iController/raw/main/%23README/0.png" width="50%" alt="">

### 2.2 macOS

> [!IMPORTANT]
> Due to the introduction of additional features starting from `v0.6.0`, it is difficult to perfectly support macOS through the non-installation method. Therefore, the packaging files for macOS are temporarily not provided, `v0.5.1` is the last stable version that supports macOS.

For `v0.5.1`, you can download from the [Release v0.5.1](https://github.com/Mehver/iController/releases/tag/v0.5.1) page.

Note: For macOS, due to permission issues, the
directly downloaded iController cannot be trusted by the system, the only solution at present is to open the switch
of `Settings > Privacy & Security > Developer Tools > Terminal`.

<img src="https://github.com/Mehver/iController/raw/main/%23README/1.jpg" width="50%" alt="">

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

Recommend use `win-onefile.bat` / `mac-onefile.sh` in `./bin/packaging/` to package the application. **Note that after testing, some Python v3.10.x versions may have
mysterious errors. Only Python v3.10.10 is recommended.**


## 4 Built With / Tech Stack

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

MPL 2.0

Copyright © 2024-PRESENT GitHub@Mehver/iController , All Rights Reserved.
