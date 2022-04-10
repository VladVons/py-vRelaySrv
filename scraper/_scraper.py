#!/usr/bin/python3 -B


import os, sys, time, json
print(os.getcwd())
sys.path.append('../src')

import json
from bs4 import BeautifulSoup
from IncP.Scheme import TScheme


def Test(aMod: str, aExt: str = '.html'):
    print(aMod, aExt)

    with open(aMod + '.json') as hFile:
        Data = hFile.read()
    Schema = json.loads(Data)

    with open(aMod + aExt) as hFile:
        Data = hFile.read()

    TimeStart = time.time()
    for i in range(1):
        Soup = BeautifulSoup(Data, 'lxml')
        #Soup = BeautifulSoup(Data, 'html.parser')

        Item = Schema['Product']
        Res = TScheme.Parse(Soup, Item)
        #Res = (dict(), set(), list())
        #Res = json.dumps(Res)
        print(Res)
    print('Time', time.time() - TimeStart)


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


os.system('clear')

#Test('empire-tech.prom.ua')
#Test('oster.com.ua')
#Test('bigmo.com.ua')
#Test('artline.ua')

Find('bigmo.com.ua')
