import PyInstaller.__main__
import shutil
import os
import time

# 假设脚本位于 ./bin/packaging/ 下，我们需要定位项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')

# 定义项目根目录下的文件和文件夹路径
main_script = os.path.join(project_root, 'main.py')
config_file = os.path.join(project_root, 'config.yaml')  # 配置文件路径
build_folder = os.path.join(project_root, 'build/')  # 前端构建文件夹路径

hooks_dir = os.path.join(project_root, 'temp_hooks')  # 临时钩子目录
os.makedirs(hooks_dir, exist_ok=True)  # 创建临时钩子目录

# 构建PyInstaller命令参数
pyinstaller_args = [
    main_script,
    # '--onefile',
    f'--add-data={config_file}{os.pathsep}.',  # 包含config.yaml
    f'--add-data={build_folder}{os.pathsep}build/',  # 包含build文件夹
    f'--additional-hooks-dir={hooks_dir}',
]

# 执行PyInstaller
PyInstaller.__main__.run(pyinstaller_args)

# 清理临时钩子目录
shutil.rmtree(hooks_dir)

# 将打包好的程序从 ./dist/main/ 移动到 ./pack-<时间戳>
dist_folder = os.path.join(project_root, 'dist/main')
pack_folder = os.path.join(project_root, f'pack-{int(time.time())}')
os.rename(dist_folder, pack_folder)

# 删除 ./dist，main.spec,，build 文件夹等
try:
    shutil.rmtree(os.path.join(project_root, 'dist'))
except Exception as e:
    pass
try:
    os.remove(os.path.join(project_root, 'main.spec'))
except Exception as e:
    pass
try:
    shutil.rmtree(os.path.join(script_dir, 'build'))
except Exception as e:
    pass

# 将打包好的程序 ./pack-<时间戳>/main 改名为 iController
os.rename(os.path.join(pack_folder, 'main'), os.path.join(pack_folder, 'iController'))

# 打包完成
print(f"打包完成！打包好的程序位于 {pack_folder} 文件夹下。")
