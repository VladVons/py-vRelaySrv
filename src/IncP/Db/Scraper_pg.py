# Created: 2022.02.18
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from Inc.UtilP.Db.ADb import TDbSql, TDbExecPool, ListToComma
from Inc.UtilP.Db.DbPg import TDbPg


class TDbApp(TDbPg):
    async def InsertUrl(self, aUrl: str, aName: str, aPrice: float, aPriceOld: float, aStock: bool, aImage: str) -> TDbSql:
        Query = f'''
            INSERT INTO url (url, name, price, price_old, on_stock, image)
            VALUES('{aUrl}', '{aName}', {aPrice}, {aPriceOld}, {aStock}, '{aImage}')
        '''
        await TDbExecPool(self.Pool).Exec(Query)

    async def AddLog(self, aType: int, aDescr: str):
        Query = f'''
            INSERT INTO log(type_id, descr)
            VALUES ({aType}, '{aDescr}')
            '''
        await TDbExecPool(self.Pool).Exec(Query)

    async def UpdateFreeTask(self, aId: int) -> TDbSql:
        Query = '''
            UPDATE
                sites
            SET
                update_date=NOW()
            WHERE
                id=%d;
            COMMIT
            ''' % (aId)
        await TDbExecPool(self.Pool).Exec(Query)

    async def SetScheme(self, aUrl: str, aScheme: str, aModerated: bool) -> TDbSql:
        Query = f'''
            update
                site
            set
                scheme = '{aScheme}',
                moderated = {aModerated},
                scheme_date = now()
            where
                (url = '{aUrl}')
            '''
        await TDbExecPool(self.Pool).Exec(Query)

    async def GetScheme(self, aEmpty: bool = False, aLimit: int = 10) -> TDbSql:
        if (aEmpty):
            CondEmpty = '(scheme is null)'
        else:
            CondEmpty = '(scheme is not null)'

        Query = f'''
           select
                id, url, scheme, protected
            from
                site
            where
                (enabled is not null) and
                (not protected) and
                {CondEmpty}
            order by
                id
            limit
                {aLimit}
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSchemeModerate(self) -> TDbSql:
        Query = '''
            select
                id, url, scheme
            from
                site
            where
                (scheme is not null) and
                (not moderated)
            order by
                id
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSiteById(self, aId: int) -> TDbSql:
        Query = f'''
           select
                id, url, scheme
            from
                site
            where
                (id = {aId})
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSiteExtById(self, aId: int) -> TDbSql:
        Query = f'''
            select
                name, data
            from
                site_ext
            where
                (enabled) and
                (site_id = {aId})
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSites(self, aLimit: int = -1) -> TDbSql:
        Limit = ''
        if (aLimit > 0):
            Limit = 'limit %s' % aLimit

        Query = f'''
            select
                id,
                url,
                scheme is not null as has_scheme,
                protected,
                enabled
            from
                site
            where
                enabled is not null
            order by
                url
            {Limit}
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSitesForUpdateFull(self, aExclId: list = None, aLimit: int = 10, aUpdDaysX: float = 1) -> TDbSql:
        if (aExclId is None):
            aExclId = []

        ExclId = ListToComma(aExclId)
        if (ExclId):
            CondExcl = 'and (not id in(%s))' % ExclId
        else:
            CondExcl = ''

        Query = f'''
            select
                id, url, sleep, scheme, sitemap
            from
                site
            where
                (enabled) and
                ((hours = '') or (hours is null) or (hours like CONCAT('%', LPAD(DATE_PART('hour', NOW())::text, 2, '0'), '%'))) and
                (DATE_PART('day', NOW() - update_date) > update_days * {aUpdDaysX})
                {CondExcl}
            order by
                update_date desc
            limit
                {aLimit}
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSitesForUpdate(self, aExclId: list = None, aCount: tuple = (0, -1), aLimit: int = 10, aUpdDaysX: float = 1) -> TDbSql:
        if (aExclId is None):
            aExclId = []

        ExclId = ListToComma(aExclId)
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
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetSiteUrlsForUpdate(self, aSiteId: int, aLimit: int = 10, aOnlyProduct: bool = False) -> TDbSql:
        if (aOnlyProduct):
            CondOnlyProduct = 'and url.product_id'
        else:
            CondOnlyProduct = ''

        Query = f'''
            select
                url.id, url.url
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
        return await TDbExecPool(self.Pool).Exec(Query)

### --- user --- ###
    async def UserAuth(self, aLogin: str, aPassw: str) -> TDbSql:
        Query = f'''
            select
                auth.id,
                auth.auth_group_id,
                auth_group.name as auth_group_name
            from
                auth
            left join auth_group on
                (auth_group.id = auth.auth_group_id)
            where
                (auth.enabled) and
                (auth.login = '{aLogin}') and
                (auth.passw = '{aPassw}')
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetUserInfo(self, aId: int) -> TDbSql:
        Query = f'''
            select
                enabled, create_date, valid_date, auth_group_id
            from
                auth
            where
                (id = {aId})
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetUserConf(self, aId) -> TDbSql:
        Query = f'''
            select
                name, data
            from
                auth_ext
            where
                (enabled) and
                (auth_id = {aId})
            '''
        return await TDbExecPool(self.Pool).Exec(Query)

    async def GetGroupConf(self, aId) -> TDbSql:
        Query = f'''
            select
                name, data
            from
                auth_group_ext
            where
                (enabled) and
                (auth_group_id = {aId})
            '''
        return await TDbExecPool(self.Pool).Exec(Query)
