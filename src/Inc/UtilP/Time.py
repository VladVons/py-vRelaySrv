# Created: 2022.10.21
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import asyncio


class TASleep():
    def __init__(self, aSleep: int = 0.05, aCnt: int = 1000):
        self.Sleep = aSleep
        self.Cnt = aCnt
        self._Cnt = 0

    async def Update(self):
        self._Cnt += 1
        if (self._Cnt % self.Cnt == 0):
            await asyncio.sleep(self.Sleep)
