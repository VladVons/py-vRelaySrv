# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# Based on aioodbc, aiomysql, aiopg


import asyncio
#
from Inc.Db.DbList import TDbList, TDbFields
from Inc.UtilP.Db.ADb import TADb


class TDbSql(TDbList):
    def __init__(self, aADb: TADb):
        super().__init__()
        self._Db = aADb

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

    def ImportDb(self, aData: tuple) -> 'TDbSql':
        self.Fields = self._GetFields(aData[1], aData[0])
        self.SetData(aData[0])
        return self

    async def Exec(self, aQuery: str, aCursor = None) -> 'TDbSql':
        if (aCursor):
            Data = await self._Db.ExecCur(aCursor, aQuery)
        else:
            Data = await self._Db.Exec(aQuery)

        if (Data):
            return self.ImportDb(Data)

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
