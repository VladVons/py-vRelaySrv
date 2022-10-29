# Created: 2022.06.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import time
import json
#
from IncP.SchemeApi import TSchemeApi
# pylint: disable-next=consider-using-from-import
import IncP.SchemeApi as SchemeApi
from Inc.Util.Mod import GetClassHelp


def GetUrlInfo(aData: dict) -> list:
    TimeAt = time.time()
    AppData = TSchemeApi.app_json(aData.get('Soup'), None)
    if (AppData):
        AppData = json.dumps(AppData, indent=2, sort_keys=True, ensure_ascii=False)

    return [
        'Source size %s' % len(aData.get('Data')),
        'Download time %.2f' % (aData['Time']),
        'Parse time %.2f' % (time.time() - TimeAt),
        '',
        'App json %s' % (AppData)
    ]

def GetApiHelp():
    Res = []
    for Api in [SchemeApi.TSchemeApi, SchemeApi.TSchemeApiExt]:
        ClassHelp = GetClassHelp(SchemeApi, Api)
        Res += [x[0] for x in ClassHelp]
    return sorted(Res)
