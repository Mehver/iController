<div align="center">
    <img src="https://github.com/Mehver/iController/raw/main/%23README/icon/256.png" width="20%"/>
    <h1>iController <code>v0.2.0</code></h1>
	<p><a href='https://github.com/Mehver/iController/blob/main/README.md'>English</a> | 简体中文</p>
</div>

## 1 描述

一个在 `Windows`/`macOS` 主机上运行的简易服务器，同一局域网下的手机连接后可以通过网页实现触摸板和键盘的操作。

### 1.1 新版本 `v0.2.X`

现在 iController 已经支持 `macOS`。

### 1.2 功能

- [x] 触摸板
- [x] 鼠标按钮（左，右，中）
- [x] 方向键
- [ ] 键盘
- [ ] 鼠标滚轮
- [ ] 触摸板双击

*部分功能尚未完成，将来会添加。*

## 2 使用方法

### 2.1 下载

从 [Release](https://github.com/Mehver/iController/releases) 页面下载。

对于 `Windows`，目前仅提供了便携式 zip 包，解压后运行 `run.bat` 即可启动，无需任何依赖。

对于 `macOS`，可以运行 `iController` 启动，同样无需任何依赖。 **注意：由于权限问题，直接下载的 iController 无法被系统信任，目前唯一的解决方法是打开 `设置 > 隐私与安全性 > 开发者工具 > 终端` 这一开关。**

启动后，手机可以根据提示访问对应地址。请确保手机与电脑之间的网络连接没有问题，如果有问题请自行调试防火墙等设置。IOS 用户建议使用 Safari 的“添加到主屏幕”功能。

### 2.2 兼容性

目前仅测试了 `Windows 10 (2024.2)`/`macOS (13.3)` 与 `IOS 17` 下的 `Safari` 浏览器，其他环境未测试。

## 3 开发

### 3.1 开发要求

- [Node.js](https://nodejs.org/en/) v16.20.2
- [Python](https://www.python.org/) v3.10.0

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

**Windows**

确保你先编译了前端（参见 3.2），然后运行 `./bin/packaging/win-zipack.bat` 打包应用。它会在仓库根目录生成一个 `pack-<timestamp>` 目录，其中包含应用程序。你可以使用 `run.bat` 启动应用程序。

**macOS**

确保你先编译了前端（参见 3.2），然后运行 `./bin/packaging/mac-pyinstaller.py` (`sudo python ./bin/packaging/mac-pyinstaller.py`) 打包应用。它会在仓库根目录生成一个 `pack-<timestamp>` 目录，其中包含应用程序。你可以使用 `iController` 启动应用程序。

## 4 使用的技术栈

- Node.js
  - React.js
    - Material UI (https://github.com/mui/material-ui)
    - Ant Design (https://github.com/ant-design/ant-design)
- Python
  - Flask (https://flask.palletsprojects.com/en/3.0.x/)
  - PyAutoGUI (https://pyautogui.readthedocs.io/en/latest/)
  - PyInstaller (*macOS only*) (https://www.pyinstaller.org/)

## 5 相似项目

- [Trackpad++](https://github.com/pg07codes/trackpadpp)
  - 作者: [pg07codes](https://github.com/pg07codes)
  - 开发语言: `JavaScript`
  - 许可证: `MIT`
  - 描述: Trackpad++ 允许使用手机作为触摸板来控制设备的光标。
  - 注: 这个项目做了类似的事情，但没有使用 PyAutoGUI，导致功能比较有限。而且已经很久没有更新了。所以我决定做一个新的。
- [AndroidTrackpad](https://github.com/teamclouday/AndroidTrackpad)
  - 作者: [teamclouday](https://github.com/teamclouday)
  - 开发语言: `C++`, `Java`
  - 许可证: `MIT`
  - 描述: 使用 Android 手机作为 Windows 或 Linux 系统的触摸板。
  - 注: 这个项目仅支持 Android，而且已经很久没有更新了。它的工作方式有点不同，它不是使用 B/S 架构，而是使用 C/S 架构，这样可能会更快，但是不够灵活。

与这些项目相比，iController 是使用 PyAutoGUI 设计的，这意味着它可以做更多的事情，而不仅仅是控制光标。但它的缺点是我没有花太多时间在跨平台支持上，而且它比 C/S 架构更卡，延迟的手感更像是远程桌面。

## 6 许可证

MPL 2.0

Copyright © 2024-PRESENT GitHub@Mehver/iController , All Rights Reserved.
