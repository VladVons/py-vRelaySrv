'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.25
License:     GNU, see LICENSE for more details

pip3 install aiopg
'''

import aiopg
#
from .Db import TDb, TDbSql
from IncP.Log import Log

class TDbPg(TDb):
    def __init__(self, aAuth: dict):
        self.Auth = aAuth

    async def Connect(self):
        await self.Close()

        AuthDef = {
            'host': self.Auth.get('Server', 'localhost'),
            'port': self.Auth.get('Port', 5432),
            'dbname': self.Auth.get('Database'),
            'user': self.Auth.get('User', 'postgres')
        }
        Log.Print(1, 'i', 'Connect()', [AuthDef])

        AuthDef['password'] = self.Auth.get('Password')
        self.Pool = await aiopg.create_pool(**AuthDef)

    async def GetTableColumns(self, aName: str) -> TDbSql:
        Query = f'''
            select
                column_name as name,
                udt_name as type
            from
                information_schema.columns
            where
                table_name = '{aName}'
            order by
                ordinal_position
            '''
        return await self.Fetch(Query)
