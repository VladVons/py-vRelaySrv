# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# Based on aioodbc, aiomysql, aiopg

import time
import asyncio
#
from IncP.Log import Log


class TADb():
    def __init__(self, aAuth: dict):
        self.Auth = aAuth # host, port, db, user, password

        self.Pool = None
        self.Debug = False
        self.Cnt = 0

    async def Connect(self):
        raise NotImplementedError()

    async def Close(self):
        if (self.Pool):
            self.Pool.close()
            await self.Pool.wait_closed()
            self.Pool = None

    async def ExecCur(self, aCursor, aSql: str) -> dict:
        TimeAt = time.time()

        self.Cnt += 1
        if (self.Debug):
            print('Cnt', self.Cnt)
            print(aSql)

        Res = {}
        try:
            await aCursor.execute(aSql)
            if (aCursor.description):
                Res['data'] = await aCursor.fetchall()
                Res['fields'] = [x.name for x in aCursor.description]
        except Exception as E:
            Res['err'] = str(E).split('\n')
            Log.Print(1, 'x', 'ExecCur() %s' % (aSql), aE=E, aSkipEcho=['TEchoDb'])

        Res['time'] = round(time.time() - TimeAt, 5)
        return Res

    async def Exec(self, aSql: str) -> dict:
        async with self.Pool.acquire() as Connect:
            async with Connect.cursor() as Cursor:
                return await self.ExecCur(Cursor, aSql)

    async def ExecFile(self, aFile: str) -> dict:
        with open(aFile, 'r', encoding = 'utf-8') as F:
            Query = F.read().strip()
            return await self.Exec(Query)

    async def ExecWait(self, aSql: str, aTimeout = 5) -> dict:
        try:
            return await asyncio.wait_for(self.Exec(aSql), timeout=aTimeout)
        except asyncio.TimeoutError:
            pass
        except Exception as E:
            Log.Print(1, 'x', 'Exec()', aE = E)

    @staticmethod
    def ListToComma(aList: list) -> str:
        Res = []
        for x in aList:
            if (isinstance(x, str)):
                Res.append(f"'{x}'")
            else:
                Res.append(str(x))
        return ', '.join(Res)
