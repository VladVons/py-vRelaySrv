# Created: 2022.10.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import re


def GetFiles(aPath: str, aMask: str = '.*', aDepth: int = 99):
    '''
    iterator function
    for x in GetFiles('/etc', '.bin$')
    '''
    if (os.path.exists(aPath)):
        for File in sorted(os.listdir(aPath)):
            Path = aPath + '/' + File
            if (os.path.isdir(Path)) and (not os.path.islink(Path)):
                if (aDepth >= 0):
                    yield from GetFiles(Path, aMask, aDepth - 1)
            else:
                if (re.search(aMask, File)):
                    yield Path

def DirRemove(aPath: str):
    for File in os.scandir(aPath):
        if (os.path.isdir(File)):
            DirRemove(File)
            os.rmdir(File)
        else:
            os.remove(File.path)