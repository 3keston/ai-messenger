import os
import subprocess

# Get the absolute path to the current script
current_dir = os.path.abspath(os.path.dirname(__file__))

# Define the path to the src directory
src_path = os.path.join(current_dir, "src")

# Define the content of the spec file with dynamic path
spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# Collect all data files
datas = collect_data_files('certifi')

a = Analysis(
    ['{src_path}/main.py'],
    pathex=['{src_path}'],
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
"""

# Define the path where the spec file will be written
spec_file_path = os.path.join(current_dir, "AIMessenger.spec")

# Write the content to the spec file
with open(spec_file_path, "w") as file:
    file.write(spec_content)

print(f"Spec file written to {spec_file_path}")

# Build the executable using the generated spec file
subprocess.run(["pyinstaller", "--noconfirm", spec_file_path])
