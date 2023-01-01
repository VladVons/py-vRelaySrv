'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.09.04
License:     GNU, see LICENSE for more details
Description:
'''


#from .Sys_files import TApi as TApiEx
from IncP.Api import TApiBase
from IncP.Api.Sys_files import TApi as TApiEx


class TApi(TApiBase):
    Param = {
        'path': '/'
    }

    async def Exec(self, aPath: str) -> str:
        Res = []
        ApiEx = TApiEx()
        Data = await ApiEx.Exec(aPath)
        for x in Data:
            Res.append('<a href=Sys_files_ls.py?path=%s&r=html>%s</a>' % (x, x))
        return '<br>'.join(Res)

    async def Query(self, aData: dict) -> str:
        return await self.ExecDef(aData, ['path'])
