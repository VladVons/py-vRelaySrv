'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.15
License:     GNU, see LICENSE for more details
Description:

https://github.com/kipe/pycron
https://crontab.guru/examples.html

Minute  Hour    DOM     Month   DOW
*       8-20    *       *       *

IsNow('*/3 6,3-5 * * 2')
'''


import time


def _Parse(aValue: str, aTarget: int) -> bool:
    for Value in aValue.split(','):
        # *
        if (aValue == '*'):
            return True
        # 3-5
        elif ('-' in Value):
            Start, End = Value.split('-')
            if (int(Start) <= aTarget <= int(End)):
                return True
        # */3
        elif ('/' in Value):
            _, Step = Value.split('/')
            if (aTarget % int(Step) == 0):
                return True
        # 2
        elif (aTarget == int(Value)):
            return True
    return False

def IsNow(aPattern: str) -> bool:
    # aPattern = '*/2 8-13 * * *'
    lt = time.localtime(time.time())
    Minute, Hour, DOM, Month, DOW = aPattern.split(' ')

    R = _Parse(Minute, lt[4]) and \
        _Parse(Hour,   lt[3]) and \
        _Parse(DOM,    lt[2]) and \
        _Parse(Month,  lt[1]) and \
        _Parse(DOW,    lt[6])
    return R

class TCron():
    #Data = [('*/2 8-13 * * *', 22), ('* 14-23 * * *', 24)]
    Data = []

    def Init(self, aData: list):
        self.Data = aData

    async def Get(self):
        for Cron, Val in self.Data:
            if (IsNow(Cron)):
                return Val
