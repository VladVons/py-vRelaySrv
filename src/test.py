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

def Test_2():
    import speedtest
    st = speedtest.Speedtest()
    serv = st.get_best_server()
    print(serv)


    #d_st = st.download()
    #print('download', int(d_st/10**6))
    #u_st = st.upload()
    #print('upload', int(u_st/10**6))
    #print('done')


def Test_3():
    from IncP.Scheme import TApi
    Param = {'Town': 'Ternopil'}
    Script = f'''
print('Hello1')
print('Hello2', Param.get('Town'))
Res = Api.split('1,2,3,4', ',')
    '''
    Res = TApi.script(Script, Param)
    print(Res)


DbAuth = {
    'Server': '192.168.2.115',
    'Database': 'scraper1',
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


async def SaveScheme():
    from IncP.DB.Scraper_pg import TDbApp

    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    Db1 = await DbApp.GetScheme(False, 1000)
    await DbApp.Close()
    print('Schemes', Db1.GetSize())
    Db1.Save('Schemes.json', not True)

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


async def Test_speed():
    from IncP.DownloadSpeed import TDownloadSpeed
    #Url = 'http://212.183.159.230/20MB.zip'
    Url = 'https://speed.hetzner.de/100MB.bin'
    await TDownloadSpeed(5).Test(Url)


print()
#asyncio.run(TestA_1())
#asyncio.run(TestA_2())
#asyncio.run(Test_pyppeteer())
#asyncio.run(Test_speed())
#asyncio.run(SaveScheme())
#Test_2()
#Test_3()


def a1(b, c, d, e, f=1, g=3, h=None, *i, j=2, k=3, **L):
    pass

def a(aFind: str, aRepl: str, aDef: str = 'Pink'):
    Arr = []
    print('123', Arr)
    return aFind.split()

q1 = a.__code__
print(1, a.__code__.co_argcount)
print(2, a.__defaults__)
print(3, a.__kwdefaults__)
print(4, a.__code__.co_kwonlyargcount)
print(5, a.__code__.co_varnames)

from IncP.Utils import GetMethodInfo
print(GetMethodInfo(a))

pass

