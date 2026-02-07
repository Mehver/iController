<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/docs/icon/256.png" width="20%" alt=""/>
    <h1>iController <code>v0.7.2</code></h1>
	<p><a href='https://github.com/Mehver/iController/blob/main/README.md'>English</a> | 简体中文</p>
    <span>
        <a href='https://github.com/Mehver/iController/releases/tag/v0.7.2'><img src="https://img.shields.io/badge/Windows%20(x64)-v0.7.2-blue?logo=data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjI1MDAiIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIiB3aWR0aD0iMjQ5MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2aWV3Qm94PSItMSAtMSAyNTggMjU5Ij48cGF0aCBkPSJNLTEtMWgyNTh2MjU5SC0xeiIvPjxwYXRoIGQ9Ik0wIDM2LjM1N0wxMDQuNjIgMjIuMTFsLjA0NSAxMDAuOTE0LTEwNC41Ny41OTVMMCAzNi4zNTh2LS4wMDF6bTEwNC41NyA5OC4yOTNsLjA4IDEwMS4wMDJMLjA4MSAyMjEuMjc1bC0uMDA2LTg3LjMwMiAxMDQuNDk0LjY3N3ptMTIuNjgyLTExNC40MDVMMjU1Ljk2OCAwdjEyMS43NGwtMTM4LjcxNiAxLjFWMjAuMjQ2ek0yNTYgMTM1LjZsLS4wMzMgMTIxLjE5MS0xMzguNzE2LTE5LjU3OC0uMTk0LTEwMS44NHoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=" alt=""/></a>&nbsp;
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

所有前端开发都在 `./frontend/` 文件夹下进行。最终通过 `npm run build` 生成静态ES6前端资源，后端在开发模式和打包时都能自动路由到build后的资源路径。

你可以在系统中配置 Node.js 环境并通过 `npm i` 来安装依赖库。更推荐的方式是直接使用本项目提供的 `./bin/DevDockerEnv/` 下的 `.bat` 或 `.sh` 脚本来一键启动官方的 Docker 环境并安装依赖。其中文件名包含 `-p3000` 的脚本会映射 3000 端口便于进行 React.js 开发调试。

**开发**

```shell
npm run react
```

**Build**

```shell
npm run build
```

### 3.3 后端

对于 Python 环境，由于此程序的目标是控制 GUI 环境下的鼠标，通过容器隔离开发环境的意义不大。因此推荐使用 [Python 的局部化虚拟环境](https://docs.python.org/zh-cn/3/library/venv.html) 来安装依赖库。推荐使用 `./bin/DevPyVenv/` 下的 `.bat` 或 `.sh` 来一键创建虚拟环境并安装依赖库到此局部虚拟环境。

你可以通过IDE绑定虚拟环境或手动进入虚拟环境。详情可见[官方文档](https://docs.python.org/zh-cn/3/library/venv.html#how-venvs-work)，具体而言：

**Windows**

```shell
venv\Scripts\activate
```

**macOS**

```shell
source venv/bin/activate
```

### 3.4 编译 / 打包

推荐直接运行 `./bin/packaging/` 中的 `win-onefile.bat` / `mac-onefile.sh` 打包应用。**注意，经过测试，部分 Python v3.10.x 版本可能会出现玄学报错。只有 Python v3.10.10 测试稳定。**

## 4 使用的技术栈

> 本项目所使用的全部依赖均为开源组件，且均基于宽松许可协议（如 MIT、BSD、Apache）。未包含任何具有传染性（如 GPL、AGPL）授权条款的组件。

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

本项目采用 BSD 3-Clause 协议开源发布。代码可以在注明出处的前提下自由使用与再发布。

本项目所使用的全部依赖均为开源组件，且均基于宽松许可协议（如 MIT、BSD、Apache）。未包含任何具有传染性（如 GPL、AGPL）授权条款的组件。

This project is released under the BSD 3-Clause License. Code may be reused with proper attribution.

Copyright (c) 2024-Present, Mehver (https://github.com/Mehver). All rights reserved.

All dependencies are open-source and licensed under permissive licenses. No copyleft (e.g., GPL, AGPL) components are included.
