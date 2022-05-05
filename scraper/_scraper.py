#!/usr/bin/python3 -B


import os, sys, time, json
print(os.getcwd())
sys.path.append('../src')

import json
from bs4 import BeautifulSoup
from IncP.Scheme import TSoupScheme


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

    TimeStart = time.time()
    for i in range(1):
        Soup = BeautifulSoup(Data, 'lxml')

        Item = Schema['Product']
        Res = TSoupScheme.Parse(Soup, Item)
        print(Res)
    print('Time', round(time.time() - TimeStart, 2))


def TestPy(aMod: str, aExt: str = '.html'):
    with open(aMod + aExt) as hFile:
        Data = hFile.read()

    Soup = BeautifulSoup(Data, 'lxml')

    Soup = Soup.find('div', {'class': 'product-view'})
    Soup = Soup.find('div', {'class': 'p-trade-price__old'})
    Soup = Soup.find('span', {'class': 'sum'})
    Soup = Soup.text
    print(Soup)


os.system('clear')
#TestJson('empire-tech.prom.ua')
#TestJson('oster.com.ua')
#TestJson('bigmo.com.ua')
#TestJson('artline.ua')
#Find('bigmo.com.ua')

#TestPy('allo.ua-a')
TestJson('allo.ua-a')