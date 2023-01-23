# Created: 2023.01.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

from Inc.Util.Obj import DeepSetByList
from .DbPg import TDbPg
from .DbSql import TDbSql


class TDbMeta():
    def __init__(self, aDb: TDbPg):
        self.Db = aDb
        self.Foreign = TForeign(self)
        self.Table = TTable(self)

    async def Init(self):
        await self.Foreign.Init()
        await self.Table.Init()

    async def Insert(self, aTable: str, aData: dict = None, aReturning: list[str] = None, aCursor = None):
        Returning = 'returning ' + ','.join(aReturning) if aReturning else ''

        if (aData):
            Fields = '(%s)' % ', '.join(aData.keys())
            Values = 'values (%s)' % self.Db.ListToComma(aData.values())
        else:
            Fields = ''
            Values = 'default values'

        Query = f'''
            insert into {aTable}
            {Fields}
            {Values}
            {Returning}
        '''
        return await TDbSql(self.Db).Exec(Query, aCursor)


class TMeta():
    def __init__(self, aParent: TDbMeta):
        self.Parent = aParent
        self.Data = {}

class TForeign(TMeta):
    async def Init(self):
        self.Data = {}
        Dbl = await self.Parent.Db.GetForeignKeys()
        for Rec in Dbl:
            Key = (Rec.GetField('table_name'), Rec.GetField('column_name'))
            Value = (Rec.GetField('table_name_f'), Rec.GetField('column_name_f'))
            DeepSetByList(self.Data, Key, Value)

    def Find(self, aTable: str, aMasters: dict, aMasterId: dict):
        Res = {}
        Data = self.Data.get(aTable, {})
        for Key, Val in Data.items():
            if (Val[0] in aMasters):
                Res[Key] = aMasterId.get(Val[0])
        return Res

class TTable(TMeta):
    async def Init(self):
        self.Data = {}
        Dbl = await self.Parent.Db.GetTableColumns()
        for Rec in Dbl:
            Key = (Rec.GetField('table_name'), Rec.GetField('column_name'))
            DeepSetByList(self.Data, Key, Rec.GetField('column_type'))
