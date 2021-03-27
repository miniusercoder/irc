import sys

import PyInstaller.__main__

name = sys.argv[1]

PyInstaller.__main__.run([
    f'{name}.py',
    f'-n{name}',
    '--onefile',
    '--clean'
])
