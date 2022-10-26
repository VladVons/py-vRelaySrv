# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import asyncio
import os
import traceback
#
from Inc.Log import TLog, TEcho, TEchoConsole, TEchoFile


class TEchoConsoleEx(TEchoConsole):
    def Write(self, aArgs: dict):
        aE = aArgs.get('aE')
        if (aE):
            traceback.print_exc()
        super().Write(aArgs)


class TEchoFileEx(TEchoFile):
    def Write(self, aArgs: dict):
        aE = aArgs.get('aE')
        if (aE):
            Lines = traceback.format_exception(aE)
            Lines.insert(0, aArgs.get('aM'))
            aArgs['aM'] = '\n'.join(Lines)
            super().Write(aArgs)
        else:
            super().Write(aArgs)

class TEchoDb(TEcho):
    def __init__(self, aDb):
        super().__init__(aType = 'ex')
        self.Db = aDb
        self.Fmt = ['aL', 'aT', 'aM', 'aD', 'aE']

    async def _Write(self, aMsg: str):
        #await self.Db.AddLog(1, aMsg)
        #ToDo
        pass

    def Write(self, aArgs: dict):
        if (aArgs.get('aL') <= self.Level) and (aArgs.get('aT') in self.Type):
            Msg = self._Format(aArgs)
            asyncio.create_task(self._Write(Msg))

Log = TLog()
