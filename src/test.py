import os
import asyncio
import random 
import time
import collections
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

def Main2():
    from Inc.DB.DbList import TDbList, TDbRec

    Db1 = TDbList( [('User', str), ('Age', int), ('Male', bool, True)] )
    Data = [['User2', 22, True], ['User1', 15, False], ['User3', 33, True], ['User1', 11, False]]
    Db1.SetData(Data)
    Db1.Sort(['User'])
    Db1.Sort(['User', 'Age'])
    print(Db1.Data)

def Main3():
    import urllib.robotparser as urobot
    rp = urobot.RobotFileParser()

    Urls = [
        'http://oster.com.ua/123.php',
        'http://oster.com.ua/images/captcha',

        'http://oster.com.ua/Asite/comp',
        'http://oster.com.ua/A/site/comp',
        'http://oster.com.ua/site/comp',
        'http://oster.com.ua?site',
        'http://oster.com.ua/?site',
        

        'http://oster.com.ua/1/comp',
        'http://oster.com.ua/comp/',
        'http://oster.com.ua/comp/1',
        'http://oster.com.ua/1/comp/',
        'http://oster.com.ua/1comp',
        'http://oster.com.ua/1/comp',

        'http://oster.com.ua/Acomp/',
        'http://oster.com.ua/cap_print/comp/',
        'http://oster.com.ua/cap_print/123.php',
        'http://oster.com.ua/call/123.php',
        'http://oster.com.ua/123.php',
        'http://oster.com.ua/captcha'
    ]
    
    #rp.set_url('http://oster.com.ua/robots.txt')
    #rp.read()
    rp.request_rate("*")

    with open('f_www.aks.ua_robots.txt') as F:
        Data = F.readlines()

        #Data = F.read()
        #Data = Data.splitlines()
        rp.parse(Data)
    
    for Url in Urls:
        if rp.can_fetch("*", Url):
            print('ok', Url)
        else:
            print('err', Url)


#async def test_open_page(url):
#    async with CloudflareScraper() as session:
#        async with session.get(url) as resp:
#            return await resp.text()


from fake_useragent import UserAgent
ua = UserAgent()
print(ua.chrome)
for i in range(30):
    print(ua.random)
