'''
Author:      Vladimir Vons, Oster Inc.
Created:     2020.02.10
License:     GNU, see LICENSE for more details
Description:.
'''


import asyncio
#
from Inc.Conf import Conf
from IncP.Log import Log


class TIdle():
    async def Run(self, aSleep: float = 10):
        CntLoop = 0
        while True:
            print('TIdle.Run', CntLoop)

            CntLoop += 1
            await asyncio.sleep(aSleep)
