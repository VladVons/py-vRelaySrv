# Created: 2023.01.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from .DbPg import TDbPg
from .DbSql import TDbSql


class TDbMeta():
    def __init__(self, aDb: TDbPg):
        self.Db = aDb
        self.Tables = {}

    async def Init(self):
        self.Tables = await self.Db.GetTables()

        Q2 = await self.Db.GetTableColumns()
        # Q3 = await self.Db.GetIndexes('ref_product')
        # Q4 = await self.Db.GetPrimaryKeys('ref_product')
        Q5 = await self.Db.GetForeignKeys()
        # Q6 = await self.Db.GetDbVersion('ref_product')

        #Q21 = await self.Db.GetForeignKeys('ref_product')
        #Q22 = await self.Db.GetForeignKeys('ref_product')

        pass

    async def Add(self, aPath: str):
        pass
