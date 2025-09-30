# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import time
import subprocess

from pathlib import Path

from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.osx import BUNDLE
from PyInstaller.building.build_main import Analysis

sys.path.append(os.path.abspath(os.getcwd()))


block_cipher = None

datas = [
   ('Assets.car', '.'),
   ('zip.png', '.'),
   ('zipd.png', '.'),
   ('AppIcon.icns', '.'),
   ('AppIcond.icns', '.'),
   ('AppIcond.png', '.'),
   ('AppIcon.png', '.'),
   ('./update/update_apply.command','./update/'),
   ('./update/restart.command','./update/'),
   ('./qss','.'),
]

a = Analysis(['Converter.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Converter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch="x86_64",
          codesign_identity=None,
          entitlements_file=None)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Converter')

app = BUNDLE(coll,
             name='Converter.app',
             icon="AppIcon.icns",
             info_plist={
                "CFBundleName": "Converter",
                "CFBundleVersion": "2.0.0",
                "CFBundleShortVersionString": "2.0.0",
                "NSHumanReadableCopyright": "2.0.0",
                "LSMinimumSystemVersion": "11.0",
                "NSRequiresAquaSystemAppearance": False,
                "NSHighResolutionCapable": True,
                "Build Date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "BuildMachineOSBuild": subprocess.run(["/usr/bin/sw_vers", "-buildVersion"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode().strip(),
                "NSPrincipalClass": "NSApplication",
                "CFBundleIconName": "Converter",
             })
