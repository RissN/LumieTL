# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = (
    collect_submodules('onnxruntime') +
    collect_submodules('cv2') +
    collect_submodules('PIL') +
    collect_submodules('PySide6') +
    ['keyring.backends.Windows']
)

datas = [
    ('assets', 'assets'),
]

a = Analysis(
    ['desktop/main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=['torch', 'torchvision', 'torchaudio'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LumieTL',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='LumieTL',
)
