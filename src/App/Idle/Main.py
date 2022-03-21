'''
Author:      Vladimir Vons, Oster Inc.
Created:     2020.02.10
License:     GNU, see LICENSE for more details
Description:
'''


import asyncio
#
from App import ConfApp
from IncP.Log import Log


class TIdle():
    async def Run(self, aSleep: float = 10):
        print('TIdle.Run', aSleep)

        CntLoop = 0
        while True:
            print('TIdle.Run.CntLoop', CntLoop)

            CntLoop += 1
            await asyncio.sleep(aSleep)
