# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# Based on aioodbc, aiomysql, aiopg


import asyncio
#
from IncP.Log import Log


class TADb():
    def __init__(self, aAuth: dict):
        self.Auth = aAuth # host, port, db, user, password

        self.Pool = None
        self.Debug = False
        self.CntGet = 0
        self.CntSet = 0

    async def Connect(self):
        raise NotImplementedError()

    async def Close(self):
        if (self.Pool):
            self.Pool.close()
            await self.Pool.wait_closed()
            self.Pool = None

    async def Exec(self, aSql: str):
        async with self.Pool.acquire() as Connect:
            async with Connect.cursor() as Cursor:
                # ToDo
                #for Sql in filter(None, aSql.split(';')):
                #    Sql = Sql.strip()
                #    if (Sql):
                #        await Cur.execute(Sql)

                self.CntSet += 1
                if (self.Debug):
                    print('CntSet', self.CntSet)
                    print(aSql)

                try:
                    await Cursor.execute(aSql)
                    if (Cursor.description):
                        Data = await Cursor.fetchall()
                        Fields = [x.name for x in Cursor.description]
                        return (Data, Fields)
                except Exception as E:
                    Log.Print(1, 'x', 'Exec() %s' % (aSql), aE=E, aSkipEcho=['TEchoDb'])
                    await asyncio.sleep(1)
            #await Connect.commit()

    async def ExecFile(self, aFile: str):
        with open(aFile, 'r', encoding = 'utf-8') as File:
            Query = File.read().strip()
            await self.Exec(Query)

    async def Fetch(self, aSql: str) -> tuple:
        async with self.Pool.acquire() as Connect:
            async with Connect.cursor() as Cursor:
            #async with Con.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as Cur:
                self.CntGet += 1
                try:
                    await Cursor.execute(aSql)
                    Data = await Cursor.fetchall()
                    Fields = [x.name for x in Cursor.description]
                    Res = (Data, Fields)
                except Exception as E:
                    Log.Print(1, 'x', 'Fetch()', aE = E)
                    Res = None

                if (self.Debug):
                    print(aSql)
                    print(Res)
                    print('CntGet', self.CntGet)
                return Res

    async def FetchWait(self, aSql: str, aTimeout = 5):
        try:
            return await asyncio.wait_for(self.Fetch(aSql), timeout=aTimeout)
        except asyncio.TimeoutError:
            pass
        except Exception as E:
            Log.Print(1, 'x', 'Exec()', aE = E)

    @staticmethod
    def ListToComma(aList: list) -> str:
        if (aList):
            if (isinstance(aList[0], str)):
                Res = ','.join('"%s"' % i for i in aList)
            elif (isinstance(aList[0], int)):
                Res = ','.join('%s' % i for i in aList)
        else:
            Res = ''
        return Res
