"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
"""

import re
import asyncio
import traceback
#
from Inc.Log import TLog, TEchoFile, TEcho


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
        await self.Db.InsertLog(1, self.TrimMsg(aMsg))

    def Write(self, aMsg: str):
        asyncio.create_task(self._Write(aMsg))


class TLogEx(TLog):
    def _DoExcept(self, aE):
        traceback.print_exc()

Log = TLogEx()
