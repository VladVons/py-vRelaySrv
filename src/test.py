import os
import asyncio
import binascii
import random
import time
from Inc.DB.DbList import TDbList, TDbRec
#
#import cfscrape
#import cloudscraper
#from aiocfscrape import CloudflareScraper
#
#from IncP.DB.Scraper_pg import TDbApp
from IncP.Log import Log


DbAuth = {
    'Server': 'localhost',
    'Database': 'test1',
    'User': 'postgres',
    'Password': '19710819'
}

async def TestA_1():
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()

    #Db1A = await DbApp.GetSitesForUpdate()
    #Db1A.Shuffle()
    #SiteId = Db1A.Rec.GetByName('site.id')

    #Db1 = await DbApp.GetSiteUrlsForUpdate(SiteId)
    #Db1 = await DbApp.GetSiteUrlsForUpdate(3)


    #q1 = await DbApp.GetTableColumns('scraper')
    #print(q1, type(q1), type(q1[0]))
    #return

    Db1 = await DbApp.GetScraper(1)

    await DbApp.Close()

    if (Db1.GetSize() > 0):
        #print()
        #print(Db1.Rec.Head)
        for Idx, Val in enumerate(Db1):
            #print(Idx, Val.Rec.GetByName('site.url'))
            #print(Val.Rec)
            print(Val.Rec.GetAsDict())

def Test_2():
    from Inc.DB.DbList import TDbList

    Fields = ['red', 'green', 'blue']
    Data = [[21, 22, 23], [11, 12, 13], [111, 121, 131], [211,221,231], [31, 32, 33]]
    Db1 = TDbList(Fields, Data)
    #Db1.SetData(Data)

    Db1.RecAdd([1,2,3])
    Db1.RecFlush()

    Db1.RecAdd()
    Db1.Rec.SetField('red', 10)
    Db1.Rec.SetField('green', 20)
    Db1.Rec.SetField('blue', 30)
    Db1.RecFlush()

    Db1.Data.append([101, 102, 103])
    Db1.RecAdd([22, 33, 44])
    Db1.RecFlush()

    Db1.RecAdd()
    Db1.Rec.SetAsDict({'red': 250, 'green': 251, 'blue': 252})
    Db1.RecFlush()

    Db1.AddList('red', [90, 91, 92, 94, 95, 96])

    Db1.RecGo(0)
    print()
    print('GetHead:', Db1.Rec.GetHead())
    print('GetSize:', Db1.GetSize())
    print('Data:', Db1.Data)
    print('Rec:', Db1.Rec)
    print('GetAsDict:', Db1.Rec.GetAsDict())
    print('GetAsTuple:', Db1.Rec.GetAsTuple())
    print('GetList:', Db1.GetList('green', True))
    print('RecPop:', Db1.RecPop())

    #Db1.Sort('green', not True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetField('red'),  Val.Rec[1])

    print()
    Db2 = Db1.Clone(['red', 'green'], (0, 2))
    Db2.Shuffle()
    for Idx, Val in enumerate(Db2):
        print(Idx, Val.Rec.GetField('red'),  Val.Rec[1])

    Db2.RecGo(-2)
    print('Db2.Rec', Db2.Rec)


def Main1():
    Start = time.time()
    for i in range(1):
        #asyncio.run(TestA_1())
        Test_2()
    print('%0.2f' % (time.time() - Start))


#async def test_open_page(url):
#    async with CloudflareScraper() as session:
#        async with session.get(url) as resp:
#            return await resp.text()

#Log.AddEcho(TEchoConsole())
#Log.Print(1, 'x', 'hello')

#Main1()


t1 = object
t2 = str
v1 = 'hello'
print(t1 , t2, type(v1) == object)
