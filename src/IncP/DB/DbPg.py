'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.25
License:     GNU, see LICENSE for more details

pip3 install aiopg
'''

import aiopg
#
from .Db import TDb, TDbSql


class TDbPg(TDb):
    def __init__(self, aAuth: dict):
        self.Auth = aAuth

    async def Connect(self):
        await self.Close()

        self.Pool = await aiopg.create_pool(
                host = self.Auth.get('Server', 'localhost'),
                port = self.Auth.get('Port', 5432),
                dbname = self.Auth.get('Database'),
                user = self.Auth.get('User'),
                password = self.Auth.get('Password')
        )

    async def GetTableColumns(self, aName: str) -> TDbSql:
        Query = f'''
            SELECT
                column_name as name
            FROM
                information_schema.columns
            WHERE
                table_name = '{aName}'
            ORDER BY
                ordinal_position
            '''
        return await self.Fetch(Query)
