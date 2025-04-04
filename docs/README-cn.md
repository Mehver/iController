<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/docs/icon/256.png" width="20%" alt=""/>
    <h1>iController <code>v0.6.5</code></h1>
	<p><a href='https://github.com/Mehver/iController/blob/main/README.md'>English</a> | 简体中文</p>
    <span>
        <a href='https://github.com/Mehver/iController/releases/tag/v0.6.5'><img src="https://img.shields.io/badge/Windows%20(x64)-v0.6.5-blue?logo=Windows" alt=""/></a>&nbsp;
        <a href='https://github.com/Mehver/iController/releases/tag/v0.5.1'><img src="https://img.shields.io/badge/MacOS%20(arm64)-v0.5.1-green?logo=Apple" alt=""/></a>&nbsp;
        <a href='https://github.com/Mehver/iController/releases/tag/v0.5.1'><img src="https://img.shields.io/badge/MacOS%20(x64)-v0.5.1-green?logo=Apple" alt=""/></a>
    </span>
</div>

## 1 描述

一个在 `Windows` 或 `macOS` (见下方注释) 主机上运行的简易服务器，同一局域网下的手机连接后可以通过网页实现触摸板和键盘的操作。

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

### 1.1 功能

- [x] 触摸板
- [x] 鼠标按钮（左，右，中）
- [x] 鼠标滚轮
- [x] 方向键
- [x] 键盘
- [x] 音量滑块

## 2 使用方法

### 2.1 下载

从 [Release](https://github.com/Mehver/iController/releases) 页面下载免安装程序。

目前程序是CLI交互的，启动时，你可以手动提供端口号，程序会自动检测确保端口可用且无冲突，启动后使用手机浏览器通过电脑的局域网IP地址和端口访问。

<img src="https://github.com/Mehver/iController/raw/main/docs/0.png" width="50%" alt="">

### 2.2 macOS

> [!IMPORTANT]
> 由于 `v0.6.0` 开始引入了额外的功能，macOS 上通过免安装的方式难以完美支持，因此暂时不再提供 macOS 版本的打包文件。目前 `v0.5.1` 将会是 macOS 一个临时的最终版本，后续版本将会首先在 Windows 上推出进行测试。

从 [Release v0.5.1](https://github.com/Mehver/iController/releases/tag/v0.5.1) 页面下载免安装程序。

注意：对于 `macOS`，由于权限问题，直接下载的 iController 无法被系统信任，目前唯一的解决方法是打开 `设置 > 隐私与安全性 > 开发者工具 > 终端` 这一开关。

<img src="https://github.com/Mehver/iController/raw/main/docs/1.jpg" width="50%" alt="">

## 3 开发

### 3.1 开发环境

- [Node.js](https://nodejs.org/en/) v16.20.2
- [Python](https://www.python.org/) v3.10.10

### 3.2 前端

**开发**

```shell
npm run react
```

**Compile**

```shell
npm run build
```

### 3.3 后端

**Windows**

对于 Python 环境，推荐使用 `./bin/dev-pyvenv/newenv.bat` 创建一个新的虚拟环境。然后运行：

```shell
venv\Scripts\activate
```

进入虚拟环境。或添加环境到IDE。

**macOS**

对于 Python 环境，推荐使用 `./bin/dev-pyvenv/newenv.sh` 创建一个新的虚拟环境。然后运行：

```shell
source venv/bin/activate
```

进入虚拟环境。或添加环境到IDE。

### 3.4 编译 / 打包

推荐直接运行 `./bin/packaging/` 中的 `win-onefile.bat` / `mac-onefile.sh` 打包应用。**注意，经过测试，部分 Python v3.10.x 版本可能会出现玄学报错。只有 Python v3.10.10 测试稳定。**

## 4 使用的技术栈

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

## 5 许可证

MPL 2.0

Copyright © 2024-PRESENT GitHub@Mehver/iController , All Rights Reserved.
