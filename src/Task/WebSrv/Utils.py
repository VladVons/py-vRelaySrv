# Created: 2022.06.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import time
import json
#
from Inc.Scheme.SchemeApi import TSchemeApi

# pylint: disable-next=consider-using-from-import
import Inc.Scheme.SchemeApi as SchemeApi
from Inc.Util.ModHelp import GetClassHelp


def GetUrlInfo(aData: dict) -> list:
    TimeAt = time.time()
    AppData = TSchemeApi.app_json(aData.get('soup'), None)
    if (AppData):
        AppData = json.dumps(AppData, indent=2, sort_keys=True, ensure_ascii=False)

    return [
        'Source size %s' % len(aData.get('data')),
        'Download time %.2f' % (aData['time']),
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
