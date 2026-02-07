# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all
qt_datas, qt_binaries, qt_hiddenimports = collect_all("PySide6")

a = Analysis(
    ['../iController.py'],
    pathex=['..'],
    binaries = qt_binaries + [],
    datas = qt_datas + [
        ('../../frontend/build', 'frontend/build/'),
        ('../HostCore', 'HostCore/'),
        ('../HostDesktopCLI', 'HostDesktopCLI/'),
        ('../HostDesktopGUI', 'HostDesktopGUI/')
    ],
    hiddenimports = qt_hiddenimports + [],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='iController',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['./assets/icon/256a.ico'],
)
