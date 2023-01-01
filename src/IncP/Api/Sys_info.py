'''
Author:      Vladimir Vons, Oster Inc.
Created:     2018.06.17
License:     GNU, see LICENSE for more details
Description:
'''


from IncP.Dev.Sys_info import TInfo


class TApi():
    async def Exec(self) -> dict:
        Data = await TInfo().Get()
        return Data[1]

    async def Query(self, aData: dict) -> dict:
        return await self.Exec()
