'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.02.18
License:     GNU, see LICENSE for more details
Description:

pip3 install aiopg
'''


import aiopg
from datetime import datetime
#
from .Db import TDb


class TDbApp(TDb):
    def __init__(self, aAuth: dict):
        self.Auth = aAuth

    async def Connect(self):
        await self.Close()

        self.Pool = await aiopg.create_pool(
                host=self.Auth.get('Server', 'localhost'),
                port=self.Auth.get('Port', 5432),
                dbname=self.Auth.get('Database'),
                user=self.Auth.get('User'),
                password=self.Auth.get('Password')
        )

    async def InsertUrl(self, aUrl: str, aName: str, aPrice: float, aPriceOld: float, aOnStock: bool, aImage: str):
            Query = '''
                INSERT INTO urls (url, name, price, price_old, on_stock, image)
                VALUES('%s', '%s', %f, %f, %d, '%s')
            ''' % (aUrl, aName, aPrice, aPriceOld, aOnStock, aImage)
            await self.Exec(Query)

    async def InsertLog(self, aType: int, aDescr: str):
        Query = '''
            INSERT INTO log(type_id, descr) 
            VALUES (%s, "%s")
        ''' % (aType, aDescr)
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
        if (aExclude): 
            Values = ','.join('%s' % i for i in aExclude)
            Exclude = 'and (not url.id in(%s))' % (Values)
        else:
            Exclude = ''

        Query = '''
        select
            url.id,
            url.url,
            url.is_product,
            site.scheme
        from
            url
        left join site on
            (url.site_id = site.id)
        where
            (site.enabled) and 
            (DATE_PART('day', NOW() - url.update_date) > site.update_days)
            {Exclude}
        ORDER BY
            random()
        limit
            {Limit}
        '''.format(Exclude=Exclude, Limit=aLimit)
        return await self.Fetch(Query)
