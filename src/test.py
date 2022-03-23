import asyncio
from IncP.DB.Scraper_pg import TDbApp

DbAuth = {
    'Server': 'localhost',
    'Database': 'test1',
    'User': 'postgres',
    'Password': '19710819'
}

async def Test_A1():
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    DbFetch = await DbApp.GetSiteUrlCountForUpdate()
    await DbApp.Close()

    print()
    print('--x1', DbFetch.GetSize())
    print('--x2', DbFetch.GetData())
    print('--x3', DbFetch.Rec)
    for Item in DbFetch:
        print(Item.AsName('site.url'), Item.AsNo(1))

asyncio.run(Test_A1())
