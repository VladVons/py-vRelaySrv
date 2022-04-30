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


async def Test_speed():
    from IncP.DownloadSpeed import TDownloadSpeed
    #Url = 'http://212.183.159.230/20MB.zip'
    Url = 'https://speed.hetzner.de/100MB.bin'
    await TDownloadSpeed(3).Test(Url)



#asyncio.run(TestA_1())
#asyncio.run(TestA_2())
#asyncio.run(Test_pyppeteer())
#asyncio.run(Test_speed())
#Test_2()

#speed_test(1)





class MyDecorator():
    def __init__(self, aFunc):
        self.Func = aFunc

    def __call__(self, *args):
        print('-----1')
        Res = self.Func(*args)
        print('-----2')
        return Res

 
@MyDecorator
def Func1(aMsg, aId):
    print("Func1()", aMsg, aId)
    return 1
 

q1 = Func1('Hello', 100)
print(q1)

