'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.19
License:     GNU, see LICENSE for more details
Description:
'''


import random
#
from IncP.Api import TApiBase


class TApi(TApiBase):
    Param = {
        'start': 0,
        'end': 10
    }

    async def Exec(self, aStart: int, aEnd: int) -> dict:
        return {'start': aStart, 'end': aEnd, 'value': random.randint(aStart, aEnd)}

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['start', 'end'])
