# -*- mode: python ; coding: utf-8 -*-
"""
LocalMind PyInstaller Spec File

Build with: pyinstaller packaging/localmind.spec
"""

import sys
from pathlib import Path

# Get the project root
SPEC_DIR = Path(SPECPATH)
PROJECT_ROOT = SPEC_DIR.parent

# Platform detection
IS_MACOS = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

# App info
APP_NAME = 'LocalMind'
APP_VERSION = '1.2.2'
APP_BUNDLE_ID = 'com.localmind.app'

# Icon paths
if IS_MACOS:
    ICON_FILE = str(PROJECT_ROOT / 'packaging' / 'macos' / 'icon.icns')
elif IS_WINDOWS:
    ICON_FILE = str(PROJECT_ROOT / 'packaging' / 'windows' / 'icon.ico')
else:
    ICON_FILE = None

# Find llama_cpp shared libraries
def get_llama_cpp_binaries():
    """Find and return llama_cpp shared libraries for bundling."""
    binaries = []
    try:
        import llama_cpp
        llama_cpp_path = Path(llama_cpp.__file__).parent
        lib_path = llama_cpp_path / 'lib'
        if lib_path.exists():
            # Get all shared libraries
            if IS_MACOS:
                libs = list(lib_path.glob('*.dylib'))
            elif IS_WINDOWS:
                libs = list(lib_path.glob('*.dll'))
            else:
                libs = list(lib_path.glob('*.so*'))

            for lib in libs:
                binaries.append((str(lib), 'llama_cpp/lib'))

        # Also check for .so files directly in llama_cpp directory
        if IS_LINUX or IS_MACOS:
            for so_file in llama_cpp_path.glob('*.so'):
                binaries.append((str(so_file), 'llama_cpp'))
    except ImportError:
        print("Warning: llama_cpp not found, skipping llama binaries")

    return binaries

llama_binaries = get_llama_cpp_binaries()

# Data files to include
datas = [
    # Report templates
    (str(PROJECT_ROOT / 'localmind' / 'reports' / 'templates'), 'localmind/reports/templates'),
    # Theme stylesheets (QSS)
    (str(PROJECT_ROOT / 'localmind' / 'resources' / 'styles'), 'localmind/resources/styles'),
    # Images and icons
    (str(PROJECT_ROOT / 'localmind' / 'resources' / 'images'), 'localmind/resources/images'),
    # Translations (i18n)
    (str(PROJECT_ROOT / 'localmind' / 'i18n' / 'translations'), 'localmind/i18n/translations'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',

    # LLM providers
    'openai',
    'anthropic',
    'llama_cpp',

    # Audio processing
    'librosa',
    'librosa.util',
    'soundfile',
    'scipy',
    'scipy.signal',
    'scipy.fft',

    # ML
    'torch',
    'torchaudio',
    'transformers',
    'huggingface_hub',

    # PDF generation
    'weasyprint',
    'jinja2',
    'matplotlib',
    'matplotlib.backends.backend_agg',

    # Whisper
    'whisper',

    # Security & validation
    'keyring',
    'keyring.backends',
    'jsonschema',

    # Utilities
    'numpy',
    'rich',
    'dotenv',
]

# Exclude unnecessary modules to reduce size
excludes = [
    'tkinter',
    'tcl',
    'tk',
    'pytest',
    'setuptools',
    'pip',
    'wheel',
]

# Binary analysis
block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / 'localmind' / 'app.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=llama_binaries,
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
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=IS_MACOS,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE if ICON_FILE and Path(ICON_FILE).exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# macOS App Bundle
if IS_MACOS:
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=ICON_FILE if ICON_FILE and Path(ICON_FILE).exists() else None,
        bundle_identifier=APP_BUNDLE_ID,
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleIdentifier': APP_BUNDLE_ID,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # Support dark mode
            'LSMinimumSystemVersion': '10.15.0',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Audio File',
                    'CFBundleTypeRole': 'Viewer',
                    'LSItemContentTypes': [
                        'public.audio',
                        'public.mp3',
                        'public.mpeg-4-audio',
                        'com.microsoft.waveform-audio',
                    ],
                },
            ],
        },
    )
