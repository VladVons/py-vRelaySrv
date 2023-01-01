'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.19
License:     GNU, see LICENSE for more details
Description:
'''


from IncP.Api import TApiBase


class TApi(TApiBase):
    Param = {
        'start': 0,
        'end': 10,
        'step': 1
    }

    Cur = 0

    async def Exec(self, aStart: int, aEnd: int, aStep: int = 1) -> dict:
        self.Cur += aStep
        if (self.Cur > aEnd):
            self.Cur = aStart

        return {'start': aStart, 'end': aEnd, 'value': self.Cur}

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['start', 'end', 'step'])
