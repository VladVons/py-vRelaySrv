# Created: 2023.01.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from Inc.Util.Obj import DeepSetByList, DeepGetByList, DeepGet
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
        return await TDbSql(self.Db).ExecCur(aCursor, Query)


class TMeta():
    def __init__(self, aParent: TDbMeta):
        self.Parent = aParent

class TForeign(TMeta):
    def __init__(self, aParent: TDbMeta):
        super().__init__(aParent)
        self.TableColumn = {}
        self.TableId = {}

    async def Init(self):
        self.TableColumn = {}
        self.TableId = {}

        Dbl = await self.Parent.Db.GetForeignKeys()
        for Rec in Dbl:
            Table = Rec.GetField('table_name')
            Column = Rec.GetField('column_name')
            TableF = Rec.GetField('table_name_f')
            ColumnF = Rec.GetField('column_name_f')

            Key = (Table, Column)
            self.TableColumn[Key] = (TableF, ColumnF)

            Key = (TableF, ColumnF)
            self.TableId[Key] = self.TableId.get(Key, {}) | {Table: Column}

    def GetColumnVal(self, aTable: str, aTableId: tuple):
        Res = {}
        if (aTableId):
            Column = self.TableId[(aTableId[0], 'id')].get(aTable)
            if (Column):
                Res[Column] = aTableId[1]
        return Res



class TTable(TMeta):
    def __init__(self, aParent: TDbMeta):
        super().__init__(aParent)
        self.Data = {}
        self.Require = {}

    async def Init(self):
        self.Data = {}
        self.Require = {}

        Dbl = await self.Parent.Db.GetTableColumns()
        for Rec in Dbl:
            Table = Rec.GetField('table_name')
            Column = Rec.GetField('column_name')
            Key = (Table, Column)
            Value = {'type': Rec.GetField('column_type'), 'null': Rec.GetField('is_null').lower()}
            DeepSetByList(self.Data, Key, Value)

            if (Value['null'] == 'no') and (Column != 'id'):
                if (Table not in self.Require):
                    self.Require[Table] = []
                self.Require[Table] += [Column]

    def Get(self, aPath: str) -> object:
        return DeepGet(self.Data, aPath)
