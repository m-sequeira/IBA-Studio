# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.datastruct import Tree

hiddenimports = collect_submodules('pyIBA')
files = Tree('/home/user/IDF_python/IBAStudio/pyIBA/pyIBA/codes/NDF_11_MS/', prefix='pyIBA/codes/NDF_11_MS/')
files = [(d[1], d[0]) for d in files]


binaries = []
datas = []

for d in files:
	if 'exe' in d[0]:
		file = d[0]
		dist = '/'.join(d[1].split('/')[:-1]) + '/'
		binaries.append((file, dist))
	elif 'zip' in d[0]:
		continue	
	else:
		file = d[0]
		dist = '/'.join(d[1].split('/')[:-1]) + '/'
		datas.append((file, dist))

for b in binaries:
	print(b)
print('datas')
for d in datas:
	print(d)

datas.append(('/home/user/IDF_python/IBAStudio/pyIBA/pyIBA/aux_files/', 'pyIBA/aux_files/'))

print('\nTo check if everything is ok run:\n diff -r pyIBA/pyIBA/codes/ dist/NDF_gui/pyIBA/codes/ \n find dist/NDF_gui/pyIBA/ -type f -not -name \'*.py\'\n')


block_cipher = None


a = Analysis(
    ['iba_studio.py'],
    pathex=[],
    binaries=binaries, #('/home/user/IDF_python/IBAStudio/pyIBA/pyIBA/codes/NDF_11_MS/NDF.exe', 'pyIBA/codes/NDF_11_MS/')
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='IBAStudio_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='IBAStudio/files',
)
