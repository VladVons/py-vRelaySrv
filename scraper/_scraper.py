#!/usr/bin/python3 -B

import os, sys
print(os.getcwd())
sys.path.append('../src')

import time, json
import asyncio
from bs4 import BeautifulSoup
#
from IncP.DB.Scraper_pg import TDbApp
from IncP.Scheme import TSoupScheme, TApi, TScheme
from IncP.Utils import FormatJsonStr


DbAuth = {
    'Server': '192.168.2.115',
    'Database': 'scraper1',
    'User': 'postgres',
    'Password': '19710819'
}


def DictHoriz(aData: object, aKeys: list, aRes: dict):
    if (type(aData) == dict):
        for Key, Val in aData.items():
            DictHoriz(Val, aKeys, aRes)
            if (Key in aKeys):
                aRes[Key] = Val

def WriteFile(aFile: str, aData: str):
    with open(aFile, 'w') as F:
        Data = F.write(aData)

def ReadFile(aFile: str):
    with open(aFile, 'r', encoding="utf-8") as hFile:
        return hFile.read()

async def SaveScheme(aFile: str):
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    Db1 = await DbApp.GetScheme(False, 1000)
    await DbApp.Close()

    print(aFile, Db1.GetSize())
    if (aFile.endswith('json')):
        Db1.Save(aFile, True)
    else:
        Arr = []
        for Rec in Db1:
            Scheme = Rec.GetField('scheme')
            if (not 'aApi.' in Scheme):
                Scheme = FormatJsonStr(Scheme)
            Arr.append('\n--- %s, %s' % (Rec.GetField('id'), Rec.GetField('url')))
            Arr.append(Scheme)
        WriteFile(aFile, '\n'.join(Arr))

def TestJson(aMod: str, aExt: str = '.html'):
    print(aMod, aExt)

    with open(aMod + '.json') as hFile:
        Data = hFile.read()
    Scheme = json.loads(Data)

    with open(aMod + aExt) as hFile:
        Data = hFile.read()

    Soup = BeautifulSoup(Data, 'lxml')
    SoupScheme = TSoupScheme()
    Res = SoupScheme.Parse(Soup, Scheme)
    print(Res)
    print()
    Arr = {}
    Res = DictHoriz(Res, ['Image', 'Price', 'Name', 'Stock', 'MPN'], Arr)
    print(Arr)

def TestPy(aMod: str, aExt: str = '.html'):
    Data = ReadFile(aMod + aExt)

    SoupA = BeautifulSoup(Data, 'lxml')
    #SoupB = BeautifulSoup(Data, 'html.parser')
    #SoupC = BeautifulSoup(Data, 'html5lib')

    #print('--x0', len(SoupA), len(SoupB), len(SoupC))

    #Soup1 = Soup.find('div', {'class': 'product-wrapper'})

    #Soup1 = Soup.find('div', {'class': 'section main-section'})
    #print('--x1', SoupA)
    #WriteFile(aMod + '.txt', str(Soup1))

    #Soup2 = Soup.find_all('div', {'class': 'product-page'})
    #print('--x2', len(Soup2))

    #Soup3 = Soup.find('script', {'type': 'application/ld+jso'})
    Soup3 = SoupA.find('script', type='application/ld+json').text
    print(Soup3)
    #Data1 = json.loads(Soup3)
    #Data2 = json.dumps(Data1, indent=2, sort_keys=True, ensure_ascii=False)
    #print('--x3', bool(Soup3), Data2)
    #WriteFile(aMod + '.txt.json', Data2)

    #Soup4 = Soup1.find('div', {'class': 'price'})
    #print('--x4', bool(Soup4))

def TestBoth(aMod: str, aExt: str = '.html'):
    #Script = ReadFile(aMod + '.txt.py')
    Script = ReadFile(aMod + '.json')
    Scheme = TScheme(Script)

    Html = ReadFile(aMod + aExt)
    Soup = BeautifulSoup(Html, 'lxml')
    Scheme.Parse(Soup)
    print(Scheme.Data)
    print(Scheme.Err)
    print('done')


def TestApi():
    Data = ReadFile('Test.json')
    Scheme = TScheme(Data)

    Data = {
        "offers": {
            "@type": "Offer",
            "availability": "http://schema.org/InStock",
            "price": "19,000.00",
            "priceCurrency": "UAH"
        }
    }

    Res = Scheme.Parse(Data)
    print(Res)



os.system('clear')
#asyncio.run(SaveScheme('Schemes.txt'))
#
#TestPy('megabit.od.ua')
#TestJson('megabit.od.ua')
TestBoth('oster.com.ua')
#TestApi()
