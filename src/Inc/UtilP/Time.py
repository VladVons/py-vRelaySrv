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

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


def SecondsToDHMS(aSeconds: int) -> dict:
    Measure = (
        ('days', 60 * 60 * 24),
        ('hours', 60 * 60),
        ('minutes', 60),
        ('seconds', 1)
    )

    Res = {}
    for Key, Val in Measure:
        Value = int(aSeconds / Val)
        if (Value):
            aSeconds -= Value * Val
            Res[Key] = Value
    return Res
