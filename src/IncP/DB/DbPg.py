# Created: 2022.02.25
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# pip3 install aiopg


import aiopg
#
from Inc.UtilP.ADb import TADb
from IncP.Log import Log


class TDbPg(TADb):
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
        return (not self.Pool.closed)

    async def GetTables(self) -> tuple:
        Query = '''
            select
                table_name
            from
                information_schema.tables
            where
                table_schema = 'public'
            '''
        return await self.Fetch(Query)

    async def GetTableColumns(self, aName: str) -> tuple:
        Query = f'''
            select
                column_name as name,
                udt_name as type,
                table_name
            from
                information_schema.columns
            where
                table_name = '{aName}'
            order by
                ordinal_position
            '''
        return await self.Fetch(Query)

    async def GetTablesColumns(self, aTable: list = None) -> dict:
        if (not aTable):
            Data = await self.GetTables()
            aTable = [x[0] for x in Data[0]]

        Res = {}
        for Table in aTable:
            Data = await self.GetTableColumns(Table)
            Names = [x[0] for x in Data[0]]
            Res[Table] = Names
        return Res
