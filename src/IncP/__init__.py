#Created:     2022.04.30
#Author:      Vladimir Vons <VladVons@gmail.com>
#License:     GNU, see LICENSE for more details


import os
import sys
import platform
#
from Inc.UtilP.Info import GetSysInfo, DictToText


__version__ = '1.0.24'
__date__ =  '2022.06.30'


#//
def GetInfo() -> dict:
    Res = {
        'Version' : __version__,
        'Date': __date__,
        'Author':  'Vladimir Vons',
        'Mail': 'VladVons@gmail.com',
        'Home': 'http://oster.com.ua',
    }
    Res.update(GetSysInfo())
    return Res

def GetInfoText():
    Data = GetInfo()
    return DictToText(Data)
