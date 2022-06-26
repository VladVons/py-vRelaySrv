import os
import asyncio
from Inc.Conf import TConf
from Inc.Log  import TLog, Log
from Inc.DB.DbList import TDbList
#
#import cfscrape
#import cloudscraper


def WriteFile(aFile: str, aData: str):
    with open(aFile, 'w') as F:
        Data = F.write(aData)

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
    from IncP.SchemeApi import TSchemeApi
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
    #Db1 = await DbApp.GetSiteExtById(2)

    UserId = 1
    DblInfo = await DbApp.GetUserInfo(UserId)
    GroupId = DblInfo.Rec.GetField('auth_group_id')
    if (GroupId):
        Dbl = await DbApp.GetGroupConf(GroupId)
        Res = Dbl.ExportPair('name', 'data')
    else:
        Res = {}

    Dbl = await DbApp.GetUserConf(UserId)
    Res.update(Dbl.ExportPair('name', 'data'))
    print(Res)
    
    Dbl = TDbList().ImportPair(Res, 'Key', ('Val', str))
    print(Dbl)

    await DbApp.Close()

    #for Idx, Rec in enumerate(Db1):
    #    print(Rec.GetAsDict())

    #print()
    #Res = Db1.ExportPair('name', 'data')
    #print(Res)


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

async def Test_GetUrl():
    from IncP.Download import TDownload, TDHeaders

    #Url = 'https://didi.ua/robots.txt'
    Url = 'https://expert24.com.ua/'
    Download = TDownload()
    Download.Opt['Headers'] = TDHeaders()
    Download.Opt['Decode'] = True
    #Download.FakeRead = True
    #Download.Timeout = None
    DataRaw = await Download.Get(Url)
    Data = DataRaw.get('Data')

    if ('checking your browser' in Data):
        print('protected')

    #print(Data)
    #WriteFile('Data1.txt', Data)
    pass


def Test_cloudscraper():
    import cloudscraper

    Url = 'https://didi.ua'
    scraper = cloudscraper.create_scraper()
    #scraper = cloudscraper.CloudScraper()
    print(scraper.get(Url).text)


def Test_TDictDef():
    import json
    from Inc.Conf import TDictDef

    DictDef = TDictDef(aData = {'One': 1})
    print(DictDef)
    print(DictDef.One, DictDef.Two, DictDef.get('Two'))

    #Data = json.dumps(DictDef)
    #print(Data)

class TClass():
    def __init__(self, aName):
        self.Name = aName

    def __enter__(self):
        print("__enter__()")
        return self

    def __exit__(self, Type, Value, Trace):
        print("__exit__()")

    def Print(self):
        print("Print()", self.Name)

#with TClass('hello') as F:
#    F.Print()
#    print("Блок внутри with")
#    #raise TypeError("Исключение TypeError")


#print()
#asyncio.run(TestA_1())
#asyncio.run(Test_pyppeteer())
#asyncio.run(Test_speed())
#asyncio.run(Test_GetUrl())
#Test_2()

#Test_cloudscraper()
#Test_TDictDef()


from IncP.SchemeApi import TSchemeApi
Str = '  \t \n\rA\xA0  '
#print(Str.strip())

#Str2 = TSchemeApi.strip(Str)
#print(Str2, len(Str2))

import re
#ReSeq_Space = r'[\s]+'
ReCmp_Strip = re.compile(r'^\s+|\s+$')

#Str2 = re.sub(r'^[\t]\w+\.four', '',  Str)
#Str2 = re.sub('^\s+|\s+$', '', Str)
Str2 = ReCmp_Strip.sub('', Str)
print(Str2, len(Str2))
