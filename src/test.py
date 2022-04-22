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


#asyncio.run(TestA_1())
#asyncio.run(Test_pyppeteer())
Log.Print(1, 'i', 'Main()', (1,2,3))
Log.Print(1, 'i', 'Run()')
