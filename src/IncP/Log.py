'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
'''


import re
import os
import asyncio
import traceback
import inspect
#
from Inc.Log import TLog, TEcho, TEchoConsole


def _GetStack(aStack) -> str:
    CurDir    = os.getcwd()
    Dir, File = os.path.split(aStack[1])
    Path   = Dir.replace(CurDir, '').strip('/') + '/' + File
    Method = aStack[3]
    Line   = aStack[2]
    return '%s %s(), line %s' % (Path, Method, Line)

def _DoExcept():
    traceback.print_exc()
    return _GetStack(inspect.stack()[2])


class TEchoConsoleEx(TEchoConsole):
    def ParseE(self, aArgs: dict):
        aE = aArgs.get('aE')
        if (aE):
            aArgs['aD'].append(aE.__class__.__name__)
            EMsg = _DoExcept()
            if (EMsg):
                aArgs['aD'].append(EMsg)

    def Write(self, aArgs: dict):
        self.ParseE(aArgs)
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
