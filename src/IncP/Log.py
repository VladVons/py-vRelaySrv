'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
'''


import re
import os
import asyncio
import traceback
import inspect
#
from Inc.Log import TLog, TEcho


class TEchoDb(TEcho):
    def __init__(self, aDb):
        super().__init__(aType = 'ex')
        self.Db = aDb

    @staticmethod
    def TrimMsg(aMsg: str) -> str:
        aMsg = aMsg.replace("'", '')
        Commas = [F.start() for F in re.finditer(',', aMsg)]
        return aMsg[Commas[3]+1 :]

    async def _Write(self, aMsg: str):
        await self.Db.AddLog(1, self.TrimMsg(aMsg))

    def Write(self, aMsg: str):
        asyncio.create_task(self._Write(aMsg))

class TLogEx(TLog):
    @staticmethod
    def _GetStack(aStack) -> str:
        CurDir    = os.getcwd()
        Dir, File = os.path.split(aStack[1])
        Path   = Dir.replace(CurDir, '').strip('/') + '/' + File
        Method = aStack[3]
        Line   = aStack[2]
        return '%s %s(), line %s' % (Path, Method, Line)

    def _DoExcept(self, aE):
        traceback.print_exc()
        return self._GetStack(inspect.stack()[2])

Log = TLogEx()
