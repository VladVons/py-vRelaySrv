# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# Based on aioodbc, aiomysql, aiopg


from Inc.Db.DbList import TDbList, TDbFields
from Inc.UtilP.Db.ADb import TADb


class TDbSql(TDbList):
    def __init__(self, aADb: TADb):
        super().__init__()
        self._Db = aADb
        self.Err = None

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

    def ImportDb(self, aData: list, aFields: list) -> 'TDbSql':
        self.Fields = self._GetFields(aFields, aData)
        self.SetData(aData)
        return self

    async def Exec(self, aQuery: str) -> 'TDbSql':
        Data = await self._Db.Exec(aQuery)
        if ('data' in Data):
            return self.ImportDb(Data['data'], Data['fields'])

    async def ExecCur(self, aCursor, aQuery: str) -> 'TDbSql':
        Data = await self._Db.ExecCur(aCursor, aQuery)
        if ('data' in Data):
            return self.ImportDb(Data['data'], Data['fields'])

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
