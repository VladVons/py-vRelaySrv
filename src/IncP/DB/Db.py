'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:

Based on aioodbc, aiomysql, aiopg
'''

import re
import asyncio
import json
import psycopg2.extras
#
from Inc.DB.DbList import TDbList
from IncP.Log  import Log


class TDbFetch(TDbList):
    def __init__(self, aDb):
        super().__init__([], [])
        self._Db = aDb

    async def _GetSelectFields(self, aQuery: str) -> list:
        Match = re.search('select(.*)from', aQuery, re.DOTALL | re.IGNORECASE)
        if (Match):
            Res = []
            for Item in  Match.group(1).split(','):
                Name = Item.strip().split()[-1]
                Arr = Name.split('.*')
                if (len(Arr) == 2):
                    Columns = await self._Db.GetTableColumns(Arr[0])
                    for Column in Columns:
                        Res.append(Column[0])
                else:
                    Res.append(Name)
            return Res

    async def Query(self, aQuery: str):
        Fields = await self._GetSelectFields(aQuery)
        Data = await self._Db.Fetch(aQuery)
        self.SetData(Data, Fields)
        return self


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
