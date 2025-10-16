# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file pour Wigor Viewer CLI.
Console executable one-file optimisé pour CI/CD.
"""

import sys
from pathlib import Path

# Configuration paths
project_root = Path(SPECPATH)
src_path = project_root / 'src'
fixtures_path = project_root / 'tests' / 'fixtures'

# Analysis configuration
a = Analysis(
    # Entry point - CLI module
    [str(src_path / 'cli.py')],
    
    # Python path includes
    pathex=[str(src_path)],
    
    # Binaries (none needed)
    binaries=[],
    
    # Data files to include
    datas=[
        # Include source modules
        (str(src_path), 'src/'),
        # Include auth modules  
        (str(project_root / 'auth'), 'auth/'),
        # Include test fixtures for smoke tests
        (str(fixtures_path), 'tests/fixtures/') if fixtures_path.exists() else None,
    ],
    
    # Hidden imports (modules not auto-detected)
    hiddenimports=[
        'src.wigor_api',
        'src.timetable_parser', 
        'src.gui',
        'src.cli',
        'auth.cookies_auth',
        # Core web dependencies
        'requests',
        'bs4',
        'beautifulsoup4',
        'soupsieve',
        'urllib3',
        'idna', 
        'charset_normalizer',
        'certifi',
    ],
    
    # Hooks
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    
    # Exclusions for CLI usage
    excludes=[
        'tkinter',
        'tkinter.ttk', 
        'tkinter.messagebox',
        'matplotlib',
        'numpy',
        'PIL',
        'pytest',
        'coverage',
    ],
    
    # Windows options
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    
    # Security
    cipher=None,
    noarchive=False,
)

# Filter out None values from datas
a.datas = [item for item in a.datas if item is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='wigor-viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)