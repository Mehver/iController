from pathlib import Path

# 应用名称和版本（标题栏会用到）
APP_NAME = "iController"

# 当前目录
BASE_DIR = Path(__file__).resolve().parent

# 应用图标（ico / png 均可，Windows 上推荐 ico）
# 建议你在 HostDesktopGUI/assets 里放一个 app.ico
APP_ICON_PATH = BASE_DIR / "assets" / "256a.ico"
