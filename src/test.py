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
    Db1A = await DbApp.GetSitesForUpdate()
    Db1A.Shuffle()
    SiteId = Db1A.Rec.GetByName('site.id')
    Db1 = await DbApp.GetSiteUrlsForUpdate(SiteId)
    await DbApp.Close()

    if (Db1.GetSize() > 0):
        print()
        #print(Db1.Rec.Head)
        for Idx, Val in enumerate(Db1):
            #print(Idx, Val.Rec.GetByName('site.url'))
            #print(Val.Rec)
            print(Val.Rec.GetAsDict())

def Test_2():
    from Inc.DB.DbList import TDbList

    Db1 = TDbList(['red', 'green', 'blue'])
    Data = [[21,22,23], [11,12,13], [111,121,131]]
    Db1.SetData(Data)

    print()
    print('GetSize:', Db1.GetSize())
    print('Data:', Db1.Data)
    print('Rec:', Db1.Rec)
    print('GetAsDict:', Db1.Rec.GetAsDict())
    print('GetAsTuple:', Db1.Rec.GetAsTuple())
    print('Json:', str(Db1))

    Db1.Sort('green', not True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetByName('red'),  Val.Rec[0])

    Db1.Add()
    Db1.Rec.SetByName('red', 11)
    Db1.Flash()

    Db1.Data.append([22,33,44])

    Db2 = Db1.Clone(['green', 'blue'])
    Db2.Shuffle()
    print('Json:', str(Db2))


asyncio.run(TestA_1())
#Test_2()
