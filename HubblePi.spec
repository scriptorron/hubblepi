# -*- mode: python ; coding: utf-8 -*-

import re, os
import PyInstaller
import shutil

block_cipher = None

################################################
# For any reason PyInstaller does not find the MKL DLLs.
# Workaround stolen from:
# https://stackoverflow.com/questions/35478526/pyinstaller-numpy-intel-mkl-fatal-error-cannot-load-mkl-intel-thread-dll

mkldir = os.path.join(PyInstaller.compat.base_prefix, "Library", "bin")
mkl_binaries = [(os.path.join(mkldir, mkl), '.') for mkl in os.listdir(mkldir) if mkl.startswith('mkl_')]

################################################
### HubblePi_Capture

Preset_files = []
Preset_SrcFolder = 'HubblePi\\capture\\presets'
for FileName in os.listdir(Preset_SrcFolder):
    if re.match("^.+\.set$", FileName):
        Preset_files.append((os.path.join(Preset_SrcFolder, FileName), 'presets'))

Capture_a = Analysis(['HubblePi\\capture\\HubblePi_Capture.py'],
             pathex=[os.path.join(os.path.abspath(SPECPATH), "HubblePi\\capture")],
             binaries=mkl_binaries,
             datas=Preset_files,
             hiddenimports=[
                "scipy.spatial.transform._rotation_groups",
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
			    #'tcl', 'tkinter', 'tornado', 'win32com',
                #'nbconvert', 'nbformat', 'IPython', 'bokeh', 'h5py', 
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
Capture_pyz = PYZ(Capture_a.pure, Capture_a.zipped_data,
             cipher=block_cipher)
Capture_exe = EXE(Capture_pyz,
          Capture_a.scripts,
          [],
          exclude_binaries=True,
          name='HubblePi_Capture',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

shutil.copyfile("build\\HubblePi\\xref-HubblePi.html", "build\\HubblePi\\xref-HubblePi_Capture.html")

################################################
### HubblePi_Viewer		  

Viewer_a = Analysis(['HubblePi\\viewer\\HubblePi_Viewer.py'],
			 pathex=[os.path.join(os.path.abspath(SPECPATH), "HubblePi\\viewer")],
             binaries=mkl_binaries,
             datas=[],
             hiddenimports=[
                "scipy.spatial.transform._rotation_groups",
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                #'nbconvert', 'nbformat', 'IPython', 'bokeh', 'h5py', 
                #'Tkconstants', 'Tkinter', 'sphinx_rtd_theme', 'notebook', 'jupyter', 'docutils', 'alabaster',
                #'h5py', 'sqlite3', 'jinja2',
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
Viewer_pyz = PYZ(Viewer_a.pure, Viewer_a.zipped_data,
             cipher=block_cipher)
Viewer_exe = EXE(Viewer_pyz,
          Viewer_a.scripts,
          [],
          exclude_binaries=True,
          name='HubblePi_Viewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

shutil.copyfile("build\\HubblePi\\xref-HubblePi.html", "build\\HubblePi\\xref-HubblePi_Viewer.html")

################################################
### HubblePi_RPi2Fits	  

RPi2Fits_a = Analysis(['HubblePi\\tools\\RPi2Fits.py'],
			 pathex=[os.path.join(os.path.abspath(SPECPATH), "HubblePi\\tools")],
             binaries=mkl_binaries,
             datas=[],
             hiddenimports=[
                "scipy.spatial.transform._rotation_groups",
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                #'nbconvert', 'nbformat', 'PyQt5', 'IPython', 'bokeh', 'h5py', 
                #'Tkconstants', 'Tkinter', 'sphinx_rtd_theme', 'notebook', 'jupyter', 'docutils', 'alabaster',
                #'h5py', 'sqlite3', 'jinja2',
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
RPi2Fits_pyz = PYZ(RPi2Fits_a.pure, RPi2Fits_a.zipped_data,
             cipher=block_cipher)
RPi2Fits_exe = EXE(RPi2Fits_pyz,
          RPi2Fits_a.scripts,
          [],
          exclude_binaries=True,
          name='HubblePi_RPi2Fits',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

shutil.copyfile("build\\HubblePi\\xref-HubblePi.html", "build\\HubblePi\\xref-HubblePi_RPi2Fits.html")

################################################
### common

coll = COLLECT(
	Capture_exe,
	Capture_a.binaries,
	Capture_a.zipfiles,
	Capture_a.datas,
	###
	Viewer_exe,
	Viewer_a.binaries,
	Viewer_a.zipfiles,
	Viewer_a.datas,
	###
	RPi2Fits_exe,
	RPi2Fits_a.binaries,
	RPi2Fits_a.zipfiles,
	RPi2Fits_a.datas,
	###	
	strip=False,
	upx=True,
	upx_exclude=[],
	name='HubblePi')
