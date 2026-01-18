# -*- mode: python ; coding: utf-8 -*-
"""
LocalMind macOS Application Spec File

Build with: pyinstaller LocalMind.spec --clean

Optimized for:
- Security: Hardened runtime, code signing ready
- Size: Excludes unnecessary modules
- Performance: UPX compression
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
    # PySide6/Qt essentials
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',

    # LocalMind modules
    'localmind',
    'localmind.config',
    'localmind.config.settings',
    'localmind.config.scoring_parameters',
    'localmind.llm',
    'localmind.llm.factory',
    'localmind.llm.base',
    'localmind.llm.local_provider',
    'localmind.reports',
    'localmind.ui',
    'localmind.ui.theme_manager',
    'localmind.ui.results_viewer',
    'localmind.ui.main_window',
    'localmind.utils',
    'localmind.workers',
    'localmind.workers.orchestrator',
    'localmind.workers.audit_worker',
    'localmind.workers.transcription_worker',
    'localmind.workers.merge_worker',

    # PyTorch essentials
    'torch.nn.functional',
    'torch._C',

    # Transformers essentials
    'transformers.models.whisper',

    # Audio processing
    'soundfile',
    'librosa',
    'scipy.signal',
]

# Exclude unnecessary modules to reduce size
excludes = [
    # Development tools
    'tkinter',
    'matplotlib',
    'IPython',
    'notebook',
    'pytest',
    'black',
    'isort',
    'ruff',
    'mypy',

    # Unused PyTorch components
    'torch.distributions',
    'torch.autograd.profiler',

    # Unused libraries
    'PIL.ImageQt',
    'PIL.ImageTk',
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
    excludes=excludes,
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
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,  # Set to Apple Developer ID for signing
    entitlements_file=None,   # Set to entitlements.plist for hardened runtime
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
    icon='localmind/resources/images/icon.icns',
    bundle_identifier='ai.localmind.desktop',
    info_plist={
        # Basic app info
        'CFBundleName': 'LocalMind',
        'CFBundleDisplayName': 'LocalMind',
        'CFBundleVersion': '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'CFBundleExecutable': 'LocalMind',
        'CFBundleIdentifier': 'ai.localmind.desktop',

        # Display settings
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'LSMinimumSystemVersion': '10.15',  # macOS Catalina+

        # Document types (audio files)
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Audio File',
                'CFBundleTypeExtensions': ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm'],
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
            }
        ],

        # Privacy permissions (required for file access)
        'NSMicrophoneUsageDescription': 'LocalMind needs microphone access to record audio for transcription.',
        'NSDesktopFolderUsageDescription': 'LocalMind needs access to save results and exports.',
        'NSDocumentsFolderUsageDescription': 'LocalMind needs access to save results and exports.',
        'NSDownloadsFolderUsageDescription': 'LocalMind needs access to save results and exports.',

        # Networking (for model downloads)
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': False,  # Security: only allow HTTPS
            'NSExceptionDomains': {
                'huggingface.co': {
                    'NSExceptionAllowsInsecureHTTPLoads': False,
                    'NSExceptionRequiresForwardSecrecy': True,
                    'NSIncludesSubdomains': True,
                },
            },
        },

        # Security
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSPrincipalClass': 'NSApplication',

        # Copyright and info
        'NSHumanReadableCopyright': 'Copyright © 2026 LocalMind. MIT License.',
        'CFBundleGetInfoString': 'LocalMind - Free, open-source AI for audio transcription and quality auditing',
    },
)
