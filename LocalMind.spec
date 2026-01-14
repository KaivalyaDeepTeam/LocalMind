# -*- mode: python ; coding: utf-8 -*-
"""
LocalMind macOS Application Spec File

Build with: pyinstaller LocalMind.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Get the current directory
ROOT = Path(SPECPATH)

# Collect data files
datas = [
    (str(ROOT / 'localmind' / 'resources'), 'localmind/resources'),
]

# Hidden imports for Qt and ML libraries
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'localmind',
    'localmind.config',
    'localmind.config.settings',
    'localmind.config.scoring_parameters',
    'localmind.llm',
    'localmind.llm.factory',
    'localmind.reports',
    'localmind.ui',
    'localmind.ui.theme_manager',
    'localmind.utils',
    'localmind.workers',
    'localmind.workers.orchestrator',
]

a = Analysis(
    [str(ROOT / 'localmind' / 'app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalMind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LocalMind',
)

app = BUNDLE(
    coll,
    name='LocalMind.app',
    icon=None,  # Add: 'localmind/resources/images/icon.icns'
    bundle_identifier='ai.localmind.desktop',
    info_plist={
        'CFBundleName': 'LocalMind',
        'CFBundleDisplayName': 'LocalMind',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.15',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Audio File',
                'CFBundleTypeExtensions': ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm'],
                'CFBundleTypeRole': 'Viewer',
            }
        ],
    },
)
