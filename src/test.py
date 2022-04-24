import os
import asyncio
from Inc.Conf import TConf
from Inc.Log  import Log
#
#import cfscrape
#import cloudscraper

DbAuth = {
    'Server': 'localhost',
    'Database': 'test1',
    'User': 'postgres',
    'Password': '19710819'
}

async def TestA_1():
    from IncP.DB.Scraper_pg import TDbApp

    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    Db1 = await DbApp.GetSiteExtById(2)
    await DbApp.Close()
    for Idx, Rec in enumerate(Db1):
        print(Rec.GetAsDict())

    print()
    Res = Db1.ExportPair('name', 'data')
    print(Res)


async def Test_pyppeteer():
    from pyppeteer import launch

    Url = 'http://oster.com.ua'
    browser = await launch()
    page = await browser.newPage()
    await page.setJavaScriptEnabled(True)
    await page.goto(Url)
    await page.screenshot({'path': 'example.png'})
    page_text = await page.content()
    await browser.close()

async def TestA_3(aArg1):
    print('TestA_3', aArg1)
    await asyncio.sleep(aArg1)
    return aArg1

async def TestA_2():
    for x in [await TestA_3(i) for i in range(10)]:
        print(x)


#asyncio.run(TestA_1())
asyncio.run(TestA_2())
#asyncio.run(Test_pyppeteer())
