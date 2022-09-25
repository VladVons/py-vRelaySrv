'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2020.02.21
License:     GNU, see LICENSE for more details
'''


import os


def FileLoad(aName: str, aMode: str = 'r') -> str:
    try:
        with open(aName, aMode) as F:
            return F.read()
    except: pass

def FileStat(aName: str) -> tuple:
    try:
        return os.stat(aName)
    except: pass

def FileExists(aName: str) -> bool:
    return FileStat(aName) is not None

def FileSize(aName: str) -> int:
    Info = FileStat(aName)
    if (Info):
        return FileStat(aName)[6]

def IsDir(aName: str) -> bool:
    Info = FileStat(aName)
    if (Info) and (Info[0] & 0x4000):
        return True

def MkDir(aName: str) -> bool:
    Path = ''
    for N in aName.split('/'):
        Path += N + '/'
        if (not FileStat(Path)):
            os.mkdir(Path[:-1])
    return IsDir(aName)
