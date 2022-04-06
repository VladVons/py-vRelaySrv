#!/usr/bin/python3 -B


import os, sys
print(os.getcwd())
sys.path.append('../src')

import json
from bs4 import BeautifulSoup
from App.Scraper.Scheme import TScheme


def Main(aMod: str, aExt: str = '.html'):
    print(aMod, aExt)

    with open(aMod + '.json') as hFile:
        Data = hFile.read()
    Schema = json.loads(Data)

    with open(aMod + aExt) as hFile:
        Data = hFile.read()
    Soup = BeautifulSoup(Data, 'lxml')

    Item = Schema['Product']
    Res = TScheme.Parse(Soup, Item)
    print(Res)


Main('empire-tech.prom.ua')
#Main('oster.com.ua')
