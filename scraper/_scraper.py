#!/usr/bin/python3 -B

import os, sys
print(os.getcwd())
sys.path.append('../src')

import time, json
from bs4 import BeautifulSoup
from IncP.Scheme import TSoupScheme, TApi, TScheme


def WriteFile(aFile: str, aData: str):
    with open(aFile, 'w') as F:
        Data = F.write(aData)

def ReadFile(aFile: str):
    with open(aFile, 'r', encoding="utf-8") as hFile:
        return hFile.read()


def Find(aMod: str, aExt: str = '.html'):
    with open(aMod + aExt) as hFile:
        Data = hFile.read()

    Soup = BeautifulSoup(Data, 'lxml')

    #Text = '626'
    #Text = '635'
    #Text = 'Адаптер PoE TP-LINK TL-PoE150S Power Over Ethernet'
    Text = 'на складе'
    #Text = 'в наличии'

    print('Find', Text)
    x11 = TScheme.GetParents(Soup, Text)

    for x1 in x11:
        for x in reversed(x1):
            print(json.dumps(x,ensure_ascii=False))
        print()

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

def TestPyScript(aMod: str, aExt: str = '.html'):
    print(aMod, aExt)

    with open(aMod + '.txt.py') as hFile:
        PyScript = hFile.read()

    with open(aMod + aExt) as hFile:
        Data = hFile.read()

    Soup = BeautifulSoup(Data, 'lxml')
    Res = TApi.script(Soup, PyScript)
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
    Scheme = TScheme(Script)

    Html = ReadFile(aMod + aExt)
    Soup = BeautifulSoup(Html, 'lxml')
    Res = Scheme.Parse(Soup)
    print(Res)

def TestApi():
    Data = ReadFile('Test.json')
    Scheme = TScheme(Data)
    Res = Scheme.Parse('One, Two, Three, Four, Five')
    print(Res)



os.system('clear')
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

TestPy('40ka.com.ua')
#TestBoth('40ka.com.ua')

#TestApi()



