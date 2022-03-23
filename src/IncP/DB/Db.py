'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:

Based on aioodbc, aiomysql, aiopg
'''

import re
import asyncio
import psycopg2.extras
#
from IncP.Log  import Log


class TDbFetch():
    def __init__(self, aDb):
        self._Db = aDb

        self.Rec = []
        self._Data = ([],[])
        self._RecNo = 0

    def __iter__(self):
        return self

    def __next__(self):
        if (self._RecNo >= self.GetSize()):
            raise StopIteration
        else:
            self._RecInit()
            self._RecNo += 1
            return self
    
    @staticmethod
    def _GetSelectFields(aQuery: str) -> list:
        Match = re.search('select(.*)from', aQuery, re.DOTALL | re.IGNORECASE)
        if (Match):
            return [Item.strip().split()[-1] for Item in Match.group(1).split(',')]

    def _RecInit(self):
        self.Rec = self.GetData()[self._RecNo]

    async def Load(self, aQuery: str):
        self._Data = (await self._Db.Fetch(aQuery), self._GetSelectFields(aQuery))
        self._RecNo = 0
        self._RecInit()
        return self

    def GetSize(self):
        return len(self._Data[0])

    def RecGo(self, aNo: int):
        self._RecNo = min(aNo, self.GetSize() - 1)
        self._RecInit()

    def GetData(self):
        return self._Data[0]

    def AsName(self, aField: str):
        Idx = self._Data[1].index(aField)
        return self.AsNo(Idx)

    def AsNo(self, aIdx: int):
        return self.Rec[aIdx]


class TDb():
    Pool = None

    def Connect(self):
        raise NotImplementedError()

    async def Close(self):
        if (self.Pool):
            self.Pool.close()
            await self.Pool.wait_closed() 
            self.Pool = None

    async def Exec(self, aSql: str):
        async with self.Pool.acquire() as Con:
            async with Con.cursor() as Cur:
                #for Sql in filter(None, aSql.split(';')):
                #    Sql = Sql.strip()
                #    if (Sql):
                #        await Cur.execute(Sql)
                await Cur.execute(aSql)
            #await Con.commit()

    async def ExecFile(self, aFile: str):
        with open(aFile, 'r') as File:
            Query = File.read().strip()
            await self.Exec(Query)

    async def Fetch(self, aSql: str, aOne: bool = False):
        async with self.Pool.acquire() as Con:
            async with Con.cursor() as Cur:
            #async with Con.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as Cur:
                #print(aSql)
                await Cur.execute(aSql)
                if (aOne):
                    Res = await Cur.fetchone()
                else:
                    Res = await Cur.fetchall()
                return Res

    async def FetchWait(self, aSql: str, aTimeout = 5):
          try:
            return await asyncio.wait_for(self.Fetch(aSql), timeout=aTimeout)
          except asyncio.TimeoutError:
            pass
          except Exception as E:
            Log.Print(1, 'x', 'Exec()', E)

    @staticmethod
    def ListToComma(aList: list) -> str:
        if (aList):
            Type = type(aList[0])
            if (Type == str):
                Res = ','.join('"%s"' % i for i in aList)
            elif (Type == int):
                Res = ','.join('%s' % i for i in aList)
        else:
            Res = ''
        return Res

