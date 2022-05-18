'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.03.05
License:     GNU, see LICENSE for more details
'''


import uasyncio as asyncio
from ucollections import deque
#
from Inc.Log  import Log


class TSender():
    def __init__(self, aOnSend, aSize: int = 10):
        self.Buf = deque((), aSize)
        self.OnSend = aOnSend

    async def Send(self, aData):
        if (await self.OnSend(aData)):
            # send unsend data
            while (len(self.Buf) > 0):
                Data = self.Buf.popleft()
                if (not await self.OnSend(Data)):
                    break
                await asyncio.sleep(0.1)
        else:
            Log.Print(1, 'i', 'UnSent', (aData))
            self.Buf.append(aData)
