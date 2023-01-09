# Created: 2022.02.25
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# pip3 install aiopg


import aiopg
#
from Inc.UtilP.ADb import TADb
from IncP.Log import Log


class TDbPg(TADb):
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

    async def GetIndexes(self, aTable: str, aSchema: str = 'public') -> tuple:
        Query = f'''
            SELECT
                i.relname,
                idxs.indexdef,
                idx.indisunique,
                t.relkind,
                array_to_string(ARRAY(
                    SELECT pg_get_indexdef(idx.indexrelid, k + 1, TRUE)
                    FROM generate_subscripts(idx.indkey, 1) AS k
                    ORDER BY k), ',')
            FROM
                pg_catalog.pg_class AS t
            INNER JOIN
                pg_catalog.pg_index AS idx
                ON (t.oid = idx.indrelid)
            INNER JOIN
                pg_catalog.pg_class AS i
                ON (idx.indexrelid = i.oid)
            INNER JOIN
                pg_catalog.pg_indexes AS idxs
                ON (idxs.tablename = t.relname AND idxs.indexname = i.relname)
            WHERE
                t.relname = {aTable} AND idxs.schemaname = {aSchema}
            ORDER BY
                idx.indisunique DESC,
                i.relname
        '''
        return await self.Fetch(Query)

    async def GetPrimaryKeys(self, aTable: str, aSchema: str = 'public') -> tuple:
        Query = f'''
            SELECT
                tc.constraint_type,
                kc.column_name
            FROM
                information_schema.table_constraints AS tc
            INNER JOIN
                information_schema.key_column_usage AS kc
                ON (tc.table_name = kc.table_name AND
                    tc.table_schema = kc.table_schema AND
                    tc.constraint_name = kc.constraint_name)
            WHERE
                tc.table_name = {aTable} AND
                tc.table_schema = {aSchema}
        '''
        return await self.Fetch(Query)

    async def GetForeignKeys(self, aTable: str, aSchema: str = 'public') -> tuple:
        Query = f'''
            SELECT DISTINCT
                kcu.column_name,
                ccu.table_name,
                ccu.column_name
            FROM
                information_schema.table_constraints AS tc
            JOIN
                information_schema.key_column_usage AS kcu
                ON (tc.constraint_name = kcu.constraint_name AND
                    tc.constraint_schema = kcu.constraint_schema AND
                    tc.table_name = kcu.table_name AND
                    tc.table_schema = kcu.table_schema)
            JOIN
                information_schema.constraint_column_usage AS ccu
                ON (ccu.constraint_name = tc.constraint_name AND
                    ccu.constraint_schema = tc.constraint_schema)
            WHERE
                tc.constraint_type = 'FOREIGN KEY' AND
                tc.table_name = {aTable} AND
                tc.table_schema = {aSchema}
            '''
        return await self.Fetch(Query)
