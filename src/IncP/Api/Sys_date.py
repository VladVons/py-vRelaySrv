'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.22
License:     GNU, see LICENSE for more details
Description:
'''


from Inc.Util.Time import GetDate, GetTime


class TApi():
    async def Exec(self) -> dict:
        return {'date': GetDate(), 'time': GetTime()}

    async def Query(self, aData: dict) -> dict:
        return await self.Exec()
