'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2020.02.24
License:     GNU, see LICENSE for more details
Description: micropython ESP8266
             DHT22 temperature-humidity sensor
'''


import machine, dht, time
import uasyncio as asyncio


class DHT22():
    def __init__(self, aPin: int):
        Pin = machine.Pin(aPin)
        self.Obj = dht.DHT22(Pin)

    async def Get(self) -> list:
        async with asyncio.Lock():
            await asyncio.sleep_ms(100)
            self.Obj.measure()
            await asyncio.sleep_ms(250)
        return (self.Obj.temperature(), self.Obj.humidity())

    def Inf(self) -> tuple:
        return ((-40, 80), (0, 100))
