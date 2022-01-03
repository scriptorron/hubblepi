# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import re, os
Preset_files = []
for FileName in os.listdir('presets'):
    if re.match("^.+\.set$", FileName):
        Preset_files.append(("presets/"+FileName, 'presets'))

a = Analysis(['HubblePi_Capture.py'],
             pathex=[os.path.abspath(SPECPATH)],
             binaries=[],
             datas=[] + Preset_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
			    'tcl', 'tkinter', 'tornado', 'win32com',
                'nbconvert', 'nbformat', 'IPython', 'bokeh', 'h5py', 
                #'Tkconstants', 'Tkinter', 'sphinx_rtd_theme', 'notebook', 'jupyter', 'docutils', 'alabaster',
                #'h5py', 'sqlite3', 'jinja2',
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='HubblePi_Capture',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='HubblePi_Capture')
