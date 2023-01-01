'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2018.06.17
License:     GNU, see LICENSE for more details
Description:
'''


import time
import uasyncio as asyncio
#
from IncP.Log import Log
from IncP.Api import TApiBase


Lock = asyncio.Lock()

class TApi(TApiBase):
    Param = {
        'delay': 1, 
        'async': True,
        'echo': True
    }

    async def Exec(self, aDelay: float, aAsync: bool, aEcho: bool) -> dict:
        async with Lock:
            if (aAsync):
                await asyncio.sleep(aDelay)
            else:
                time.sleep(aDelay)

            R = {'delay': aDelay, 'async': aAsync, 'echo': aEcho}
            if (aEcho):
                Log.Print(1, 'i', 'sys_sleep', R)
            return R

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['delay', 'async', 'echo'])
