import asyncio
import binascii
import random
from IncP.DB.Scraper_pg import TDbApp


DbAuth = {
    'Server': 'localhost',
    'Database': 'test1',
    'User': 'postgres',
    'Password': '19710819'
}

async def TestA_1():
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    DbFetch = await DbApp.GetSiteUrlCountForUpdate()
    await DbApp.Close()

    for Item in DbFetch:
        print(Item.Rec.GetByName('site.url'), Item.Rec[1])

def Test_2():
    from Inc.DB.DbList import TDbList

    Data = [[1,2,3], [10,20,30], [110,120,130]]
    Db = TDbList(['red', 'green', 'blue'])
    Db.SetData(Data)

    print()
    print('GetSize', Db.GetSize())
    print('Data', Db.Data)
    print('Rec', Db.Rec)
    print('Json', str(Db))
    for Item in Db:
        print(Item.Rec.GetByName('red'),  Item.Rec[0])

    Db.Add()
    Db.Rec.SetByName('red', 11)
    Db.Flash()

    Db.Data.append([22,33,44])

    print('GetData', Db.GetData([0, 1]))


asyncio.run(TestA_1())
#Test_2()
