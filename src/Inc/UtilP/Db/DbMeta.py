# Created: 2023.01.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

from Inc.Util.Obj import DeepSetByList
from .DbPg import TDbPg
from .DbSql import TDbSql


class TDbMeta():
    def __init__(self, aDb: TDbPg):
        self.Db = aDb
        self.Tables = {}
        self.Foreign = {}

    async def InitForeign(self):
        self.Foreign = {}
        Dbl = await self.Db.GetForeignKeys()
        for Rec in Dbl:
            Value = [Rec.GetField('table_name_f'), Rec.GetField('column_name_f')]
            DeepSetByList(self.Foreign, [Rec.GetField('table_name'), Rec.GetField('column_name')], Value)

    async def Init(self):
        await self.InitForeign()

        #self.Tables = await self.Db.GetTables()
        #Q2 = await self.Db.GetTableColumns()
        # Q3 = await self.Db.GetIndexes('ref_product')
        # Q4 = await self.Db.GetPrimaryKeys('ref_product')
        # Q6 = await self.Db.GetDbVersion('ref_product')

        #Q21 = await self.Db.GetForeignKeys('ref_product')
        #Q22 = await self.Db.GetForeignKeys('ref_product')

        pass

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
