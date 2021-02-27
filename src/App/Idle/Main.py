'''
Author:      Vladimir Vons, Oster Inc.
Created:     2020.02.10
License:     GNU, see LICENSE for more details
Description:.
'''


import asyncio
#
from Inc.Conf import Conf
from Inc.Log  import Log


class TIdle():
    async def Run(self, aSleep: float = 2):
        CntLoop = 0
        while True:
            Log.Print(1, 'i', 'TIdle.Run', CntLoop)

            CntLoop += 1
            await asyncio.sleep(aSleep)
