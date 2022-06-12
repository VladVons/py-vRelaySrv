'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details

Based on aioodbc, aiomysql, aiopg
'''

import asyncio
#import psycopg2.extras
#
from Inc.DB.DbList import TDbList, TDbFields
from IncP.Log import Log


class TDbSql(TDbList):
    def __init__(self, aDb):
        super().__init__()
        self._Db = aDb

    def _GetFields(self, aFields: list, aData: list) -> TDbFields:
        Res = TDbFields()
        Data = aData[0] if (aData) else None
        Res.AddAuto(aFields, Data)
        return Res

    def _GetInsertStr(self, aTable: str):
        Fields = [Val[0] for Key, Val in self.Fields.IdxOrd.items()]
        Values = [Rec.GetAsSql() for Rec in self]
        return 'insert into %s (%s) values (%s)' % (aTable, ', '.join(Fields), '), ('.join(Values))

    def _GetUpdate(self, aTable: str, aRecNo: int = 0):
        self.RecNo = aRecNo
        return 'update %s set %s' % (aTable, self.Rec.GetAsSql())

    async def Fetch(self, aQuery: str):
        Data, Fields = await self._Db.Fetch(aQuery)
        self.Fields = self._GetFields(Fields, Data)
        self.SetData(Data)
        return self

    async def Insert(self, aTable: str):
        Query = self._GetInsertStr(aTable)
        await self._Db.Exec(Query)

    async def InsertUpdate(self, aTable: str, aUniqField: str):
        Insert = self._GetInsertStr(aTable)
        Set = [
            '%s = excluded.%s' % (Key, Key)
            for Key in self.Fields
            if (Key != aUniqField)
        ]
        Set = ', '.join(Set)

        Query = f'''
            {Insert}
            on conflict ({aUniqField}) do update
            set {Set}
            returning id;
        '''
        return await self._Db.Exec(Query)


class TDb():
    Pool = None
    Debug = False
    CntGet = 0
    CntSet = 0

    def Connect(self):
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
        with open(aFile, 'r') as File:
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
            Type = type(aList[0])
            if (Type == str):
                Res = ','.join('"%s"' % i for i in aList)
            elif (Type == int):
                Res = ','.join('%s' % i for i in aList)
        else:
            Res = ''
        return Res
