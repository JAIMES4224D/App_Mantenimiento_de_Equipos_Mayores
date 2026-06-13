# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para mtto_pro
Genera un ejecutable Windows (.exe) independiente sin dependencias externas
"""

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Recopilar módulos y datos
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'bcrypt',
    'sqlite3',
]

datas = [
    # Incluir assets si existen
    # ('assets', 'assets'),
]

a = Analysis(
    ['app.py'],
    pathex=['d:\\Proyectos\\mtto_pro'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mtto_pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola (GUI puro)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Opcional: agregar ícono con icon='ruta/icono.ico'
)
