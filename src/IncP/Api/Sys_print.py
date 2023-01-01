'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2018.06.17
License:     GNU, see LICENSE for more details
Description:
'''


from Inc.Http.HttpUrl import UrlPercent
from IncP.Api import TApiBase


class TApi(TApiBase):
    Param = {
        'text': 'hello'
    }

    async def Exec(self, aText: str) -> dict:
        aText = UrlPercent(bytes(aText, 'utf8'))
        print(aText)
        return {'Text': aText}

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['text'])
