# -*- mode: python -*-

block_cipher = None


a = Analysis(['QM_demo.py'],
             pathex=['C:\\Users\\Cam Feenstra\\Documents\\QM_demo'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='QM_demo',
          debug=False,
          strip=False,
          upx=True,
          console=False )
