# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['HubblePi_Viewer.py'],
             pathex=['C:\\MyFiles\\Projekte\\HubblePi_Copy\\HubblePi_Viewer'],
             binaries=[],
             datas=[],
             hiddenimports=[
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                'nbconvert', 'nbformat', 'PyQt5', 'IPython', 'bokeh', 'h5py', 
                'Tkconstants', 'Tkinter', 'sphinx_rtd_theme', 'notebook', 'jupyter', 'docutils', 'alabaster',
                'h5py', 'sqlite3', 'jinja2',
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
          name='HubblePi_Viewer',
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
               name='HubblePi_Viewer')
