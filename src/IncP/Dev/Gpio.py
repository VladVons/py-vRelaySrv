'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.12.22
License:     GNU, see LICENSE for more details
Description:
'''


from machine import Pin
import uasyncio as asyncio


class GpioW():
    def __init__(self, aPin: int):
        self.Obj = Pin(aPin, Pin.OUT)
        self.Lock = asyncio.Lock()

    async def Set(self, aVal: int):
        async with self.Lock:
            self.Obj.value(aVal)

    async def Get(self):
        async with self.Lock:
            return self.Obj.value()
