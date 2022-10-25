# Created: 2020.02.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import asyncio


class TIdle():
    async def Run(self, aSleep: float = 10):
        CntLoop = 0
        while True:
            print(f'TIdle.Run.CntLoop({aSleep}) {CntLoop}')

            CntLoop += 1
            await asyncio.sleep(aSleep)
