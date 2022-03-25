'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.02.18
License:     GNU, see LICENSE for more details
Description:

pip3 install aiopg
'''


import aiopg
from .Db import TDb, TDbFetch


class TDbApp(TDb):
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

    async def InsertUrl(self, aUrl: str, aName: str, aPrice: float, aPriceOld: float, aOnStock: bool, aImage: str):
            Query = f'''
                INSERT INTO url (url, name, price, price_old, on_stock, image)
                VALUES('{aUrl}', '{aName}', {aPrice}, {aPriceOld}, {aOnStock}, '{aImage}')
            '''
            await self.Exec(Query)

    async def InsertLog(self, aType: int, aDescr: str):
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

    async def GetUrlForUpdate(self, aExclude: list = [], aLimit: int = 10):
        Exclude = self.ListToComma(aExclude)
        if (Exclude): 
            Exclude = 'and (not url.id in(%s))' % Exclude

        Query = f'''
            select
                url.id,
                url.url,
                site.scheme
            from
                url
            left join site on
                (url.site_id = site.id)
            where
                (site.enabled) and 
                (DATE_PART('day', NOW() - url.update_date) > site.update_days)
                {Exclude}
            order by
                url.update_date
            limit
                {aLimit}
        '''
        return await TDbFetch(self).Query(Query)

    async def GetSitesForUpdate(self, aExclude: list = [], aLimit: int = 10):
        Exclude = self.ListToComma(aExclude)
        if (Exclude): 
            Exclude = 'and (not site.id in(%s))' % Exclude

        Query = f'''
           Select
                site.id,
                site.url,
                site.sleep,
                site.tasks,
                site.scheme,
                count(*) as url_count,
                sum(data_size) as data_size
            from
                url
            left join site on
                (url.site_id = site.id)
            where
                (site.enabled) and
                (DATE_PART('day', NOW() - url.update_date) > site.update_days)
                {Exclude}
            group by
                site.id
            order by
                url_count
            limit
                {aLimit}
        '''
        return await TDbFetch(self).Query(Query)
