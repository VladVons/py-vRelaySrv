'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2018.06.17
License:     GNU, see LICENSE for more details
Description:
'''


import sys
import uasyncio as asyncio
#
from IncP.Api import TApiBase


class TApi(TApiBase):
    Param = {
        'delay': 1
    }

    async def Exec(self, aDelay: int = 1) -> dict:
        await asyncio.sleep(aDelay)
        sys.exit()

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['delay'])
