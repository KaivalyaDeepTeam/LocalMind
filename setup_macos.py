"""
LocalMind macOS Application Builder

Run with: python setup_macos.py py2app
"""

from setuptools import setup
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from localmind import __version__, __app_name__

APP = ['localmind/app.py']
DATA_FILES = [
    ('resources/styles', [
        'localmind/resources/styles/theme_light.qss',
        'localmind/resources/styles/theme_dark.qss',
    ]),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,  # Add icon path here: 'localmind/resources/images/icon.icns'
    'plist': {
        'CFBundleName': __app_name__,
        'CFBundleDisplayName': __app_name__,
        'CFBundleVersion': __version__,
        'CFBundleShortVersionString': __version__,
        'CFBundleIdentifier': 'ai.localmind.desktop',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'LSMinimumSystemVersion': '10.15',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Audio File',
                'CFBundleTypeExtensions': ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm'],
                'CFBundleTypeRole': 'Viewer',
            }
        ],
    },
    'packages': [
        'localmind',
        'localmind.config',
        'localmind.llm',
        'localmind.reports',
        'localmind.ui',
        'localmind.utils',
        'localmind.workers',
        'PySide6',
        'torch',
        'transformers',
        'faster_whisper',
        'pyannote',
    ],
    'includes': [
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    'excludes': [
        'tkinter',
        'matplotlib.backends.backend_tkagg',
    ],
    'resources': [
        'localmind/resources',
    ],
}

setup(
    name=__app_name__,
    version=__version__,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
