'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2018.06.17
License:     GNU, see LICENSE for more details
Description:
'''


import os
#
from IncP.Api import TApiBase
from Inc.Util.FS import IsDir


class TApi(TApiBase):
    Param = {
        'path': '/'
    }

    async def Exec(self, aPath: str) -> list:
        Res = []
        Files = sorted(os.listdir(aPath))
        for x in Files:
            Path = aPath + '/' + x
            if (IsDir(Path)):
                Path += '/'
            Res.append(Path)
        return Res

    async def Query(self, aData: dict) -> list:
        return await self.ExecDef(aData, ['path'])
