import os
import asyncio
import random 
import time
import operator
from aiohttp import web
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

s1 = '1234'
print(float(s1))
