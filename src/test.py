import os
import asyncio
from Inc.Conf import TConf
from Inc.Log  import TLog, Log
#
#import cfscrape
#import cloudscraper


def Test_1():
    from pympler.asizeof import asizeof 

    print()
    print('None', asizeof(None))
    print('int', asizeof(3))
    print('float', asizeof(3.14))
    print('string', asizeof('1'))
    print('tuple', asizeof((1)))
    print('list', asizeof([1]))
    print('dict', asizeof({'1': 1}))
    print('set', asizeof(set()))
    print('Log', asizeof(TLog))

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
    import async_timeout
    async with async_timeout.timeout(5):
        await asyncio.sleep(3)
        print('ok')
    print('end')

#asyncio.run(TestA_1())
asyncio.run(TestA_2())
#asyncio.run(Test_pyppeteer())

