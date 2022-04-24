'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:

Based on aioodbc, aiomysql, aiopg
'''

import re
import asyncio
#import psycopg2.extras
#
from Inc.DB.DbList import TDbList, TDbFields
from IncP.Log import Log


class TDbSql(TDbList):
    def __init__(self, aDb):
        super().__init__()
        self.Safe = False
        self._Db = aDb

    async def _GetSelectFields(self, aQuery: str) -> list:
        # ToDo
        if ('from' in aQuery.lower()):
            Pattern = 'select(.*)from'
        else:
            Pattern = 'select(.*)'

        Match = re.search(Pattern, aQuery, re.DOTALL | re.IGNORECASE)
        if (Match):
            Res = []
            for Item in  Match.group(1).split(','):
                Name = Item.strip().split()[-1]
                Arr = Name.split('.*')
                if (len(Arr) == 2):
                    Columns = await self._Db.GetTableColumns(Arr[0])
                    for Column in Columns:
                        Res.append(Column[0])
                # skip comma inside functions
                elif (not [x for x in '()' if (x in Name)]):
                    Res.append(Name)
            return Res

    async def Query(self, aQuery: str):
        Data = await self._Db.Fetch(aQuery)
        Fields = await self._GetSelectFields(aQuery)

        self.Fields = TDbFields()
        if (Data):
            self.Fields.Auto(Fields, Data[0])
        self.SetData(Data)
        return self

    def GetInsertStr(self, aTable: str):
        Fields = [Val[0] for Key, Val in self.Fields.IdxOrd.items()]
        Values = [Rec.GetAsSql() for Rec in self]
        return 'INSERT INTO %s (%s) VALUES (%s)' % (aTable, ', '.join(Fields), '), ('.join(Values))

    async def Insert(self, aTable: str):
        Query = self.GetInsertStr(aTable)
        await self._Db.Exec(Query)

class TDb():
    Pool = None
    Debug = False

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
                # ToDo
                #for Sql in filter(None, aSql.split(';')):
                #    Sql = Sql.strip()
                #    if (Sql):
                #        await Cur.execute(Sql)
                if (self.Debug):
                    print(aSql)

                try:
                    await Cur.execute(aSql)
                except Exception as E:
                    Log.Print(1, 'x', 'Exec() %s' % (aSql), aE=E, aSkipEcho=['TEchoDb'])
                    asyncio.sleep(1)
            #await Con.commit()

    async def ExecFile(self, aFile: str):
        with open(aFile, 'r') as File:
            Query = File.read().strip()
            await self.Exec(Query)

    async def Fetch(self, aSql: str):
        async with self.Pool.acquire() as Con:
            async with Con.cursor() as Cur:
            #async with Con.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as Cur:
                if (self.Debug):
                    print(aSql)

                try:
                    await Cur.execute(aSql)
                    return await Cur.fetchall()
                except Exception as E:
                    Log.Print(1, 'x', 'Fetch()', aE = E)

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
            Type = type(aList[0])
            if (Type == str):
                Res = ','.join('"%s"' % i for i in aList)
            elif (Type == int):
                Res = ','.join('%s' % i for i in aList)
        else:
            Res = ''
        return Res
