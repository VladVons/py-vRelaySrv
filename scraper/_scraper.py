#!/usr/bin/python3 -B

import os, sys
import asyncio
#
print(os.getcwd())
sys.path.append('../src')

import time, json
from bs4 import BeautifulSoup
from IncP.Scheme import TSoupScheme, TApi, TScheme
from IncP.DB.Scraper_pg import TDbApp


def WriteFile(aFile: str, aData: str):
    with open(aFile, 'w') as F:
        Data = F.write(aData)

def ReadFile(aFile: str):
    with open(aFile, 'r', encoding="utf-8") as hFile:
        return hFile.read()

async def SaveScheme():
    DbAuth = {
        'Server': '192.168.2.115',
        'Database': 'scraper1',
        'User': 'postgres',
        'Password': '19710819'
    }
    File = 'Schemes.json'

    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    Db1 = await DbApp.GetScheme(False, 1000)
    await DbApp.Close()
    print(File, Db1.GetSize())
    Db1.Save(File, True)

def TestJson(aMod: str, aExt: str = '.html'):
    print(aMod, aExt)

    with open(aMod + '.json') as hFile:
        Data = hFile.read()
    Schema = json.loads(Data)

    with open(aMod + aExt) as hFile:
        Data = hFile.read()

    Soup = BeautifulSoup(Data, 'lxml')

    Item = Schema['Product']
    Res = TSoupScheme.Parse(Soup, Item)
    print(Res)

def TestPy(aMod: str, aExt: str = '.html'):
    Data = ReadFile(aMod + aExt)
    Soup = BeautifulSoup(Data, 'lxml')

    Soup1 = Soup.find('div', {'id': 'main_content'})
    print('--x1', bool(Soup))
    #WriteFile(aMod + '.txt', str(Soup1))

    #Soup2 = Soup.find_all('div', {'class': 'product-page'})
    #print('--x2', len(Soup2))

    #Soup3 = Soup.find('script', {'type': 'application/ld+jso'})
    Soup3 = Soup1.find('script', type='application/ld+json').text
    Data1 = json.loads(Soup3)
    Data2 = json.dumps(Data1, indent=2, sort_keys=True, ensure_ascii=False)
    print('--x3', bool(Soup3), Data2)
    WriteFile(aMod + '.txt.json', Data2)


    #Soup4 = Soup1.find('div', {'class': 'price'})
    #print('--x4', bool(Soup4))

def TestBoth(aMod: str, aExt: str = '.html'):
    Script = ReadFile(aMod + '.txt.py')
    #Script = ReadFile(aMod + '.json')
    Scheme = TScheme(Script)

    Html = ReadFile(aMod + aExt)
    Soup = BeautifulSoup(Html, 'lxml')
    Scheme.Parse(Soup)
    print(Scheme.Data)
    print(Scheme.Err)


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
#asyncio.run(SaveScheme())

#TestJson('empire-tech.prom.ua')
#TestJson('oster.com.ua')
#TestJson('bigmo.com.ua')
#TestJson('artline.ua')
#Find('bigmo.com.ua')

#TestPy('allo.ua-a')
#TestJson('allo.ua-a')

#TestPy('can.ua')
#TestJson('can.ua')
#TestPyScript('can.ua')
TestBoth('can.ua')


#TestPy('40ka.com.ua')
#TestBoth('40ka.com.ua')

#TestApi()
