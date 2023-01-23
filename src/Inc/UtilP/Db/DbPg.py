# Created: 2022.02.25
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# pip3 install aiopg


import aiopg
#
from Inc.UtilP.Db.ADb import TADb
from Inc.UtilP.Db.DbSql import TDbSql
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

    async def GetTables(self, aSchema: str = 'public') -> TDbSql:
        Query = f'''
            select
                table_name
            from
                information_schema.tables
            where
                table_schema = '{aSchema}'
            order by
                table_name
            '''
        return await TDbSql(self).Exec(Query)

    async def GetTableColumns(self, aTable: str = '', aSchema: str = 'public') -> TDbSql:
        CondTable = f"and table_name = '{aTable}'" if (aTable) else ''

        Query = f'''
            select
                table_name,
                column_name,
                udt_name as column_type
            from
                information_schema.columns
            where
                table_schema = '{aSchema}'
                {CondTable}
            order by
                table_name,
                column_name
            '''
        return await TDbSql(self).Exec(Query)

    async def GetIndexes(self, aTable: str = '', aSchema: str = 'public') -> TDbSql:
        CondTable = f"and t.relname = '{aTable}'" if (aTable) else ''

        Query = f'''
            select
                t.relname as table_name,
                i.relname,
                idxs.indexdef,
                idx.indisunique,
                t.relkind,
                array_to_string(array(
                    select pg_get_indexdef(idx.indexrelid, k + 1, true)
                    from generate_subscripts(idx.indkey, 1) as k
                    order by k), ',')
            from
                pg_catalog.pg_class as t
            inner join
                pg_catalog.pg_index as idx
                on (t.oid = idx.indrelid)
            inner join
                pg_catalog.pg_class as i
                on (idx.indexrelid = i.oid)
            inner join
                pg_catalog.pg_indexes as idxs
                on (idxs.tablename = t.relname and idxs.indexname = i.relname)
            where
                (idxs.schemaname = '{aSchema}')
                {CondTable}
            order by
                idx.indisunique desc,
                i.relname
        '''
        return await TDbSql(self).Exec(Query)

    async def GetPrimaryKeys(self, aTable: str = '', aSchema: str = 'public') -> TDbSql:
        CondTable = f"and tc.table_name = '{aTable}'" if (aTable) else ''

        Query = f'''
            select
                tc.table_name,
                kc.column_name,
                tc.constraint_type
            from
                information_schema.table_constraints as tc
            inner join
                information_schema.key_column_usage as kc
                on (tc.table_name = kc.table_name and
                    tc.table_schema = kc.table_schema and
                    tc.constraint_name = kc.constraint_name)
            where
                tc.table_schema = '{aSchema}'
                {CondTable}
        '''
        return await TDbSql(self).Exec(Query)

    async def GetForeignKeys(self, aTable: str = '', aSchema: str = 'public') -> TDbSql:
        CondTable = f"and tc.table_name = '{aTable}'" if (aTable) else ''

        Query = f'''
            select distinct
                tc.table_name,
                kcu.column_name,
                ccu.table_name as table_name_f,
                ccu.column_name as column_name_f
            from
                information_schema.table_constraints as tc
            join
                information_schema.key_column_usage as kcu
                on (tc.constraint_name = kcu.constraint_name and
                    tc.constraint_schema = kcu.constraint_schema and
                    tc.table_name = kcu.table_name and
                    tc.table_schema = kcu.table_schema)
            join
                information_schema.constraint_column_usage as ccu
                on (ccu.constraint_name = tc.constraint_name and
                    ccu.constraint_schema = tc.constraint_schema)
            where
                tc.constraint_type = upper('foreign key')
                and tc.table_schema = '{aSchema}'
                {CondTable}
            '''
        return await TDbSql(self).Exec(Query)

    async def GetDbVersion(self, aSchema: str = 'public') -> TDbSql:
        Query = f'''
            select
                current_database() as db_name,
                version() as version,
                date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime,
                pg_database_size(current_database()) as size,
                (
                    select
                        count(*) as count
                    from
                        information_schema.tables
                    where
                        (table_catalog = current_database())
                        and (table_schema = '{aSchema}')
                ) as tables
            '''
        return await TDbSql(self).Exec(Query)
