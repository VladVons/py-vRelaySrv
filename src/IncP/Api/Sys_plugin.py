'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.19
License:     GNU, see LICENSE for more details
Description:
'''


from Inc.Plugin import Plugin


class TApi():
    async def Exec(self) -> dict:
        return list(Plugin.keys())

    async def Query(self, aData: dict) -> dict:
        return await self.Exec()
