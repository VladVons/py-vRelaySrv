#!/usr/bin/python3 -B


import os, sys, time
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

    TimeStart = time.time()
    for i in range(1):
        Soup = BeautifulSoup(Data, 'lxml')
        #Soup = BeautifulSoup(Data, 'html.parser')

        Item = Schema['Product']
        Res = TScheme.Parse(Soup, Item)
        print(Res)
    print('Time', time.time() - TimeStart)



#Main('empire-tech.prom.ua')
#Main('oster.com.ua')
#Main('bigmo.com.ua')
Main('artline.ua')
