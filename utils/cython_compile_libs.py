#!/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import shutil
import sys

from pyximport.pyxbuild import pyx_to_dll

WD = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
LIBS = os.path.join(WD, 'libs')
# Adds the libs directory to the path
sys.path.append(LIBS)

import common


def main():
    filelist = common.parseFileList([LIBS], recursive=True)
    try:
        import pefile
        filepath = pefile.__file__[:-1]
        filelist.append(filepath)
    except ImportError:
        print('pefile not installed...')
    for filename in filelist:
        if filename.endswith('.py'):
            filename = str(filename)
            try:
                pyx_to_dll(filename, inplace=True)
                print(filename, 'successful!')
            except Exception as e:
                print('ERROR:', filename, 'failed')
            try:
                os.remove(filename[:-2] + 'c')
            except Exception as e:
                # TODO: log exception
                pass

    # Cleanup build dirs
    walk = os.walk(LIBS)
    for path in walk:
        path = path[0]
        if os.path.basename(path) == '_pyxbld' and os.path.isdir(path):
            shutil.rmtree(path)


if __name__ == '__main__':
    main()
