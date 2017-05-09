import os
a = Analysis(['butler.py'],
             pathex=[os.path.abspath('.')],
             hiddenimports=['mysql.connector.locales.eng.client_error'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='butler.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True, icon='ausbutler.ico', version='.version')
