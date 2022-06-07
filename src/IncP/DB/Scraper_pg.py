'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.18
License:     GNU, see LICENSE for more details
'''


import aiopg
#
from .Db import TDbSql
from .DbPg import TDbPg


class TDbApp(TDbPg):
    async def InsertUrl(self, aUrl: str, aName: str, aPrice: float, aPriceOld: float, aStock: bool, aImage: str):
            Query = f'''
                INSERT INTO url (url, name, price, price_old, on_stock, image)
                VALUES('{aUrl}', '{aName}', {aPrice}, {aPriceOld}, {aStock}, '{aImage}')
            '''
            await self.Exec(Query)

    async def AddLog(self, aType: int, aDescr: str):
        Query = f'''
            INSERT INTO log(type_id, descr)
            VALUES ({aType}, '{aDescr}')
            '''
        await self.Exec(Query)

    async def UpdateFreeTask(self, aId: int):
        Query = '''
            UPDATE
                sites
            SET
                update_date=NOW()
            WHERE
                id=%d;
            COMMIT;
            ''' % (aId)
        await self.Exec(Query)

    async def SetScheme(self, aId: int, aScheme: str):
        Query = f'''
            update
                site
            set
                scheme = '{aScheme}'
            where
                (id = {aId})
            '''
        await self.Exec(Query)

    async def GetDbVersion(self) -> TDbSql:
        Query = f'''
            select
                current_database() as name,
                version() as version,
                date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime,
                pg_database_size(current_database()) as size,
                (select count(*) as count
                    from information_schema.tables
                    where (table_catalog = current_database()) and (table_schema = 'public')
                ) as tables
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetScheme(self, aEmpty: bool = False, aLimit: int = 10) -> TDbSql:
        if (aEmpty):
            CondEmpty = '(site.scheme is null)'
        else:
            CondEmpty = '(site.scheme is not null)'

        Query = f'''
           select
                id,
                url,
                scheme
            from
                site
            where
                (enabled is not null) and
                {CondEmpty}
            order by
                id
            limit
                {aLimit}
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetSiteById(self, aId: int) -> TDbSql:
        Query = f'''
           select
                id,
                url,
                scheme
            from
                site
            where
                (id = {aId})
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetSiteExtById(self, aId: int) -> TDbSql:
        Query = f'''
            select
                name,
                data
            from
                site_ext
            where
                (enabled) and
                (site_id = {aId})
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetSites(self, aLimit: int = -1) -> TDbSql:
        Limit = ''
        if (aLimit > 0):
            Limit = 'limit %s' % aLimit

        Query = f'''
            select
                site.id,
                site.url,
                site.scheme is not null as has_scheme,
                site.enabled
            from
                site
            order by
                site.url
            {Limit}
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetSitesForUpdateFull(self, aExclId: list = [], aLimit: int = 10, aUpdDaysX: float = 1) -> TDbSql:
        ExclId = self.ListToComma(aExclId)
        if (ExclId):
            CondExcl = 'and (not site.id in(%s))' % ExclId
        else:
            CondExcl = ''

        Query = f'''
            select
                site.id,
                site.url,
                site.sleep,
                site.scheme,
                site.sitemap
            from
                site
            where
                (site.enabled) and
                ((site.hours = '') or (site.hours is null) or (site.hours like CONCAT('%', LPAD(DATE_PART('hour', NOW())::text, 2, '0'), '%'))) and
                (DATE_PART('day', NOW() - site.update_date) > site.update_days * {aUpdDaysX})
                {CondExcl}
            order by
                site.update_date desc
            limit
                {aLimit}
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetSitesForUpdate(self, aExclId: list = [], aCount: tuple = (0, -1), aLimit: int = 10, aUpdDaysX: float = 1) -> TDbSql:
        ExclId = self.ListToComma(aExclId)
        if (ExclId):
            CondExcl = 'and (not site.id in(%s))' % ExclId
        else:
            CondExcl = ''

        CountMin, CountMax = aCount
        if (CountMin < CountMax):
            CondCount =  '(count(*) between %d and %d)' % (CountMin, CountMax)
        else:
            CondCount = '(count(*) > %d)' % CountMin

        Query = f'''
            select
                site.id,
                site.url,
                site.sleep,
                site.scheme,
                site.sitemap,
                count(*) as url_count,
                sum(data_size) as data_size
            from
                url
            left join site on
                (url.site_id = site.id)
            where
                (site.enabled) and
                ((site.hours = '') or (site.hours is null) or (site.hours like CONCAT('%', LPAD(DATE_PART('hour', NOW())::text, 2, '0'), '%'))) and
                (DATE_PART('day', NOW() - url.update_date) > site.update_days * {aUpdDaysX})
                {CondExcl}
            group by
                site.id
            having
                {CondCount}
            order by
                url_count desc
            limit
                {aLimit}
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetSiteUrlsForUpdate(self, aSiteId: int, aLimit: int = 10, aOnlyProduct: bool = False) -> TDbSql:
        if (aOnlyProduct):
            CondOnlyProduct = 'and url.product_id'
        else:
            CondOnlyProduct = ''

        Query = f'''
            select
                url.id,
                url.url
            from
                url
            left join site on
                (url.site_id = site.id)
            where
                (site.enabled) and
                ((site.hours = '') or (site.hours is null) or (site.hours like CONCAT('%', LPAD(DATE_PART('hour', NOW())::text, 2, '0'), '%'))) and
                (url.site_id = {aSiteId}) and
                (DATE_PART('day', NOW() - url.update_date) > site.update_days)
                {CondOnlyProduct}
            order by
                url.update_date
            limit
                {aLimit}
            '''
        return await TDbSql(self).Fetch(Query)

    async def AuthUser(self, aLogin: str, aPassw: str) -> TDbSql:
        Query = f'''
            select
                id
            from
                auth
            where
                (enabled) and
                (login = '{aLogin}') and
                (passw = '{aPassw}')
            '''
        return await TDbSql(self).Fetch(Query)

    async def GetUserConfig(self, aId: int) -> TDbSql:
        Query = f'''
            select
                workers,
                enabled
            from
                auth
            where
                (id = '{aId}')
            '''
        return await TDbSql(self).Fetch(Query)
