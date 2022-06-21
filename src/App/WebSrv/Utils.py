'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.20
License:     GNU, see LICENSE for more details
'''

import time
import json
#
from IncP.SchemeApi import TSchemeApi


def GetUrlInfo(aData: dict) -> list:
    TimeAt = time.time()
    AppData = TSchemeApi.app_json(aData.get('Soup'))
    if (AppData):
        AppData = json.dumps(AppData, indent=2, sort_keys=True, ensure_ascii=False)

    return [
        'Source size %s' % len(aData.get('Data')),
        'Download time %.2f' % (aData['Time']),
        'Parse time %.2f' % (time.time() - TimeAt),
        '',
        'App json %s' % (AppData)
    ]
