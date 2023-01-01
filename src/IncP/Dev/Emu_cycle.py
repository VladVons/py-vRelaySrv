'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.19
License:     GNU, see LICENSE for more details
Description:
'''


import time


class TCycle():
    def __init__(self, aStart: int, aEnd: int, aStep: float = 1.0):
        self.Start = self.Cur = aStart
        self.End = aEnd
        self.Step = aStep

    async def Get(self) -> list:
        self.Cur += self.Step
        if (self.Cur > self.End):
            self.Cur = self.Start

        return [self.Cur, time.time()]
