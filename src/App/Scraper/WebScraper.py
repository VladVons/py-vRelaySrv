'''
VladVons@gmail.com
2022.02.17

cat /etc/tor/torrc
ExitNodes {ua}, {ru}, {by}, {su}, {pl}, {md}, {bg} StrictNodes 0
MaxCircuitDirtiness 1

https://b3rn3d.herokuapp.com/blog/2014/03/05/tor-country-codes
https://ipinfo.io/json'

https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b
torify curl https://brain.com.ua
torify wget --user-agent=mozilla --output-document=brain-proxy.html https://brain.com.ua 

UrlChekIP = 'http://icanhazip.com'
'''


import os
import asyncio
import aiohttp
import random
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from aiohttp_socks import ProxyConnector
#
from IncP.Log import Log
from IncP.Download import TDownload
from IncP.DB.Scraper_pg import TDbApp
from .Scheme import TScheme

class TWebScraper():
    def __init__(self, aParent, aScheme: dict, aSleep: int = 1):
        self.Sleep = aSleep
        self.Scheme = aScheme
        self.Parent = aParent

        self.TotalData = 0
        self.TotalUrl = 0
        self.IsRun = False

        self.Download = TDownload(self.Parent.Conf.get('Proxy', []))
        self.Queue = asyncio.Queue()

        self.Event = asyncio.Event()
        self.Wait(False)

    async def _DoUrl(self, aUrl: str, aData, aStatus: int):
        raise NotImplementedError()

    def Wait(self, aEnable: bool):
        if  (aEnable):
            self.Event.clear()
        else:
            self.Event.set()

    def Stop(self):
        self.Wait(False)
        self.IsRun = False

    async def _Worker(self):
        await asyncio.sleep(random.randint(5))
   
        TimeStart = time.time()
        self.IsRun = True
        while (self.IsRun):
            await self.Event.wait()
            await asyncio.sleep(random.randint(int(self.Sleep / 2), self.Sleep))

            if (self.Queue.empty()) and (time.time() - TimeStart > 10):
                break

            try:
                Url = await asyncio.wait_for(self.Queue.get(), 10)
                Arr = await self.Download.Get(Url)
                if (Arr):
                    Data, Status = Arr
                    if (Status == 200):
                        self.TotalData += len(Data)
                        self.TotalUrl += 1
                    await self._DoUrl(Url, Data, Status)
                self.Queue.task_done()
            except (aiohttp.ClientConnectorError, aiohttp.ClientError, asyncio.TimeoutError, Exception) as E:
                Log.Print(1, 'x', '_Worker(). %s' % (Url), aE = E)
        Log.Print(1, 'i', '_Worker(). done')

class TWebScraperFull(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrlRoot: str, aSleep: int = 1):
        super().__init__(aParent, aScheme, aSleep)

        self.UrlRoot = aUrlRoot
        self.Url = []
        self.Queue.put_nowait(aUrlRoot)

    @staticmethod
    def IsMimeApp(aUrl: str) -> bool:
        Path = urlparse(aUrl).path
        Ext = os.path.splitext(Path)[1]
        return Ext in ['.zip', '.rar', '.xml', '.pdf', '.jpg', '.jpeg', '.png', '.gif']

    async def _DoUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = BeautifulSoup(aData, "lxml")
        for A in Soup.find_all("a"):
            Href = A.get("href", '').strip().rstrip('/')
            if (Href):
                if (Href.startswith('/')):
                    Href = self.UrlRoot + Href

                if (Href.startswith(self.UrlRoot)) and \
                   (not Href.startswith('#')) and \
                   (not Href in self.Url) and \
                   (not self.IsMimeApp(Href)):
                    self.Url.append(Href)
                    self.Queue.put_nowait(Href)
                    #Log.Print(1, 'i', '_GrabHref(). Add url %s' % (Href))
        await self._GrabHref(aUrl, Soup, aStatus)

    async def _GrabHref(self, aUrl: str, aSoup: BeautifulSoup, aStatus: int):
        Msg = 'task:%2d, status:%d, found:%2d, done:%d, total:%dM, %s ;' % (aStatus, len(self.Url), self.TotalUrl, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)

        Res = TScheme.Parse(aSoup, self.Scheme)
        if (Res):
            self.UrlScheme += 1
            #print('---x1', Res)
            #await self.Parent.Db.InsertUrl(aUrl, Res.get('Name', ''), Res.get('Price', 0), Res.get('PriceOld', 0), Res.get('OnStock', 1), Res.get('Image', ''))


class TWebScraperUpdate(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrls: list, aSleep: int):
        super().__init__(aParent, aScheme, aSleep)
        
        for Url in aUrls:
            self.Queue.put_nowait(Url)

    async def _DoUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = BeautifulSoup(aData, "lxml")

        Msg = 'task:%2d, status:%d, found:%2d, done:%d, total:%dM, %s ;' % (aStatus, self.TotalUrl, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)
