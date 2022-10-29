# Created: 2022.04.30
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import sys
import time
import platform
#
from Inc.UtilP.Time import SecondsToDHMS_Str

TimeStart = time.time()


def GetSysInfo() -> dict:
    UName =  platform.uname()
    Res = {
        'App': os.path.basename(sys.argv[0]).rsplit('.')[0],
        'OS': f'{UName.system}, {UName.release}, {UName.processor}',
        'Host': UName.node,
        'User': os.environ.get('USER'),
        'Python': (sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        'UptimeSys': SecondsToDHMS_Str(time.monotonic()),
        'UptimeApp': SecondsToDHMS_Str(time.time() - TimeStart),
        'Now': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return Res

def DictToText(aData: dict) -> str:
    Arr = [f'{Key}: {Val}' for Key, Val in aData.items()]
    return '\n'.join(Arr)
