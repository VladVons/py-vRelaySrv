'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:.

Based on aioodbc, aiomysql
'''


import asyncio
import psycopg2.extras
#
from IncP.Log  import Log


class TDb():
    Pool = None

    def Connect(self):
        raise NotImplementedError()

    async def Close(self):
        if (self.Pool):
            self.Pool.terminate()
            await self.Pool.wait_closed()
            self.Pool = None

    async def Exec(self, aSql: str):
        async with self.Pool.acquire() as Con:
            async with Con.cursor() as Cur:
                for Sql in filter(None, aSql.split(';')):
                    Sql = Sql.strip()
                    if (Sql):
                        await Cur.execute(Sql)
            #await Con.commit()

    async def ExecFile(self, aFile: str):
        with open(aFile, 'r') as File:
            Query = File.read().strip()
            await self.Exec(Query)

    async def Fetch(self, aSql: str, aOne: bool = False):
        async with self.Pool.acquire() as Con:
            #async with Con.cursor() as Cur:
            async with Con.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as Cur:
                await Cur.execute(aSql)
                if (aOne):
                    return await Cur.fetchone()
                else:
                    return await Cur.fetchall()

    async def FetchWait(self, aSql: str, aTimeout = 5):
          try:
            return await asyncio.wait_for(self.Fetch(aSql), timeout=aTimeout)
          except asyncio.TimeoutError:
            pass
          except Exception as E:
            Log.Print(1, 'x', 'Exec()', E)

