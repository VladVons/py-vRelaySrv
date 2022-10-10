'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.10.10
License:     GNU, see LICENSE for more details
'''


import os
import re


def GetFiles(aPath: str, aMask: str = '.*', aDepth: int = 99) -> list[str]:
    Res = []
    if (os.path.exists(aPath)):
        for File in sorted(os.listdir(aPath)):
            Path = aPath + '/' + File
            if (os.path.isfile(Path)):
                if (re.search(aMask, File)):
                    Res.append(Path)
            elif (aDepth >= 0):
                Res += GetFiles(Path, aMask, aDepth - 1)
    return Res
