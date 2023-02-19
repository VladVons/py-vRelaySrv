# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# Based on aioodbc, aiomysql, aiopg

import time
import asyncio
#
from IncP.Log import Log
from Inc.DbList import TDbSql


def ListToComma(aData: list) -> str:
    Res = []
    for x in aData:
        if (isinstance(x, str)):
            Res.append(f"'{x}'")
        else:
            Res.append(str(x))
    return ', '.join(Res)

def ListIntToComma(aData: list[int]) -> str:
    return ', '.join(map(str, aData))


class TADb():
    def __init__(self, aAuth: dict):
        self.Auth = aAuth # host, port, db, user, password
        self.Pool = None

    async def Connect(self):
        raise NotImplementedError()

    async def Close(self):
        if (self.Pool):
            self.Pool.close()
            await self.Pool.wait_closed()
            self.Pool = None


class TDbExec():
    Debug = False

    async def _Exec(self, aSql: str) -> dict:
        raise NotImplementedError()

    async def _ExecToDbl(self, aSql: str) -> TDbSql:
        Data = await self._Exec(aSql)
        if ('data' in Data):
            return TDbSql(Data['fields'], Data['data'])

    async def ExecCurTry(self, aCursor, aSql: str) -> dict:
        TimeAt = time.time()

        try:
            Res = await self.ExecCurs(aCursor, aSql)
        except Exception as E:
            Res = {'err': str(E).split('\n', maxsplit = 1)[0]}
            Log.Print(1, 'x', 'ExecCurTry() %s' % (aSql), aE=E, aSkipEcho=['TEchoDb'])

        Res['time'] = round(time.time() - TimeAt, 5)
        return Res

    async def ExecCurs(self, aCursor, aSql: str) -> dict:
        if (self.Debug):
            print(aSql)

        Res = {}
        await aCursor.execute(aSql)
        if (aCursor.description):
            Data = await aCursor.fetchall()
            Fields = [x.name for x in aCursor.description]
            Res = {'data': Data, 'fields': Fields}
        return Res

    async def ExecFile(self, aFile: str) -> dict:
        with open(aFile, 'r', encoding = 'utf-8') as F:
            Query = F.read().strip()
            return await self._ExecToDbl(Query)

    async def ExecWait(self, aSql: str, aTimeout = 5) -> dict:
        try:
            return await asyncio.wait_for(self._ExecToDbl(aSql), timeout=aTimeout)
        except asyncio.TimeoutError:
            pass
        except Exception as E:
            Log.Print(1, 'x', 'ExecWait()', aE = E)

    async def Exec(self, aSql: str) -> TDbSql:
        return await self._ExecToDbl(aSql)


class TDbExecPool(TDbExec):
    def __init__(self, aPool):
        self.Pool = aPool

    async def _Exec(self, aSql: str) -> dict:
        async with self.Pool.acquire() as Connect:
            async with Connect.cursor() as Cursor:
                return await self.ExecCurTry(Cursor, aSql)

class TDbExecCurs(TDbExec):
    def __init__(self, aCursor):
        self.Cursor = aCursor

    async def _Exec(self, aSql: str) -> dict:
        return await self.ExecCurs(self.Cursor, aSql)
