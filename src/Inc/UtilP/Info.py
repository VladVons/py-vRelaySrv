# Created: 2022.04.30
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import sys
import time
import platform
#
from Inc.UtilP.Time import SecondsToDHMS


def GetSysInfo() -> dict:
    Uptime = SecondsToDHMS(time.monotonic())
    Uptime = [f'{Val} {Key}' for Key, Val in Uptime.items()]

    UName =  platform.uname()
    Res = {
        'App': os.path.basename(sys.argv[0]).rsplit('.')[0],
        'OS': UName.system,
        'Host': UName.node,
        'User': os.environ.get('USER'),
        'Python': (sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        'Uptime': ', '.join(Uptime),
        'Now': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return Res

def DictToText(aData: dict) -> str:
    Arr = [f'{Key}: {Val}' for Key, Val in aData.items()]
    return '\n'.join(Arr)
