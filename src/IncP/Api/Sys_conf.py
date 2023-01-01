'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.06
License:     GNU, see LICENSE for more details
Description:
'''


from App import ConfApp

class TApi():
    async def Exec(self) -> dict:
        return ConfApp

    async def Query(self, aData: dict) -> dict:
        return await self.Exec()
