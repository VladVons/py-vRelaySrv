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
        self._Db = aDb

    def _GetFields(self, aData: list, aDescr: tuple) -> TDbFields:
        if (aData):
            Res = TDbFields()
            for i in range(len(aData[0])):
                Res.Add(aDescr[i].name, type(aData[0][i]))
            return Res

    async def Query(self, aQuery: str):
        Data, Descr = await self._Db.Fetch(aQuery)
        self.Fields = self._GetFields(Data, Descr)
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
                    await asyncio.sleep(1)
            #await Con.commit()

    async def ExecFile(self, aFile: str):
        with open(aFile, 'r') as File:
            Query = File.read().strip()
            await self.Exec(Query)

    async def Fetch(self, aSql: str, aAll = True):
        async with self.Pool.acquire() as Connect:
            async with Connect.cursor() as Cursor:
            #async with Con.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as Cur:
                if (self.Debug):
                    print(aSql)

                try:
                    await Cursor.execute(aSql)
                    if (aAll):
                        Res = await Cursor.fetchall()
                    else:
                        Res = await Cursor.fetchone()
                    return (Res, Cursor.description)
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
