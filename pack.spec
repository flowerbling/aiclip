# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# 指定数据文件
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('algorithm_model', 'algorithm_model'),
    ('ffmpeg', 'ffmpeg'),
    ('wordninja_gz', 'wordninja')
]

# 指定二进制文件
binaries = []

# 指定隐藏导入
hiddenimports = []

# 使用collect_all来收集特定包的依赖
for module in [
    'paddle', 
    'PIL', 
    'shapely', 
    'paddleocr', 
    'pyclipper', 
    'imghdr', 
    'skimage', 
    'imgaug', 
    'scipy', 
    'lmdb', 
    'numpy', 
    'Cython'
]:
    tmp_ret = collect_all(module)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

# 分析你的应用
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    bundle_identifier='com.imnight.aigc',
    icon="static/logo.png",
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 创建Pyz文件
pyz = PYZ(a.pure)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIClip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    author="imnight",
    copyright='Copyright (C) 2024 IMNIGHT',
    icon="static/logo.webp"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='智能视频剪辑工具',
    icon="static/logo.webp"
)