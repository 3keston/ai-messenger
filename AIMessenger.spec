# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# Collect all data files
datas = collect_data_files('certifi')

a = Analysis(
    ['/Users/keston/Github/xerolith/src/main.py'],
    pathex=['/Users/keston/Github/xerolith/src'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'aiosqlite', 'anyio', 'certifi', 'h11', 'httpcore',
        'httpx', 'idna', 'ollama', 'pytypedstream',
        'sniffio', 'typing_extensions'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIMessenger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False if it's a GUI app
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='path/to/icon.icns'  # Use an .icns file for macOS icon
)

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AIMessenger.app'  # Output as a .app bundle for macOS
)
