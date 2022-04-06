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
import re
import gzip
import asyncio
import aiohttp
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup
#
from IncP.Log import Log
from IncP.Download import TDownload
from Inc.DB.DbList import TDbList
from .Scheme import TScheme
from .Api import Api


class TSender():
    def __init__(self, aParent: 'TWebScraper', aMaxSize: int = 3):
        self.Parent = aParent
        self.MaxSize = aMaxSize
        self.Dbl = TDbList([
            ('Url', str), 
            ('Name', str), 
            ('Price', float), 
            ('Currency', str), 
            ('PriceOld', float), 
            ('Image', str), 
            ('Stock', bool),
            ('SKU', str)
        ])

    async def Add(self, aData: dict):
        self.Dbl.RecAdd()
        self.Dbl.Rec.SetAsDict(aData)
        if (self.Dbl.GetSize() > self.MaxSize):
            await self.Flush()

    async def Flush(self):
        if (not self.Dbl.IsEmpty()):
            Data = self.Dbl.DataExport()
            SrvRes = await Api.SendResult(Data)
            if (SrvRes):
                self.Dbl.Empty()


class TWebScraper():
    def __init__(self, aParent, aScheme: dict, aSleep: int = 1):
        self.Sleep = aSleep
        self.Scheme = aScheme
        self.Parent = aParent

        self.TotalData = 0
        self.TotalUrl = 0
        self.UrlScheme = 0
        self.IsRun = False

        #self.Download = TDownload(self.Parent.Conf.get('Proxy', []))
        self.Download = TDownload()
        self.DblQueue = TDbList( [('Url', str)] )
        self.Sender = TSender(self)

        self.Event = asyncio.Event()
        self.Wait(False)

    async def _DoWorkerUrl(self, aUrl: str, aData, aStatus: int):
        raise NotImplementedError()

    async def _DoWorkerStart(self):
        pass

    async def _DoWorkerEnd(self):
        pass

    def Wait(self, aEnable: bool):
        if  (aEnable):
            self.Event.clear()
        else:
            self.Event.set()

    def Stop(self):
        self.Wait(False)
        self.IsRun = False

    async def _Worker(self):
        await self._DoWorkerStart()

        #await asyncio.sleep(random.randint(1, 5))
        self.IsRun = True
        while (self.IsRun) and (not self.DblQueue.IsEmpty()):
            await self.Event.wait()

            try:
                Rec = self.DblQueue.RecPop()
                Url = Rec.GetField('Url')
                Arr = await self.Download.Get(Url)
                if (Arr):
                    Data, Status = Arr
                    if (Status == 200):
                        self.TotalData += len(Data)
                        self.TotalUrl += 1
                    await self._DoWorkerUrl(Url, Data, Status)
            except (aiohttp.ClientConnectorError, aiohttp.ClientError, asyncio.TimeoutError, Exception) as E:
                Log.Print(1, 'x', '_Worker(). %s' % (Url), aE = E)

            await asyncio.sleep(random.randint(int(self.Sleep / 2), self.Sleep))

        await self.Sender.Flush()
        await self._DoWorkerEnd()
        Log.Print(1, 'i', '_Worker(). done')


class TWebScraperFull(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrlRoot: str, aSleep: int = 1):
        super().__init__(aParent, aScheme, aSleep)

        self.UrlRoot = aUrlRoot
        self.Url = []
        self.DblQueue.RecAdd([aUrlRoot])

    @staticmethod
    def IsMimeApp(aUrl: str) -> bool:
        Path = urlparse(aUrl).path
        Ext = os.path.splitext(Path)[1]
        return Ext in ['.zip', '.rar', '.xml', '.pdf', '.jpg', '.jpeg', '.png', '.gif']

    async def _DoWorkerUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = BeautifulSoup(aData, 'lxml')
        Htrefs = Soup.find_all('a')
        for A in Htrefs:
            Href = A.get('href', '').strip().rstrip('/')
            if (Href):
                if (Href.startswith('/')):
                    Href = self.UrlRoot + Href

                if (Href.startswith(self.UrlRoot)) and \
                   (not Href.startswith('#')) and \
                   (not Href in self.Url) and \
                   (not self.IsMimeApp(Href)):
                    self.Url.append(Href)
                    self.DblQueue.RecAdd([Href])
                    #Log.Print(1, 'i', '_GrabHref(). Add url %s' % (Href))
        await self._GrabHref(aUrl, Soup, aStatus)

    async def _GrabHref(self, aUrl: str, aSoup: BeautifulSoup, aStatus: int):
        Msg = 'status:%d, found:%2d, done:%d, total:%dM, %s ;' % (aStatus, len(self.Url), self.TotalUrl, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)

        Res = TScheme.Parse(aSoup, self.Scheme)
        if (Res):
            self.UrlScheme += 1
            #print('---x1', Res)
            #await self.Parent.Db.InsertUrl(aUrl, Res.get('Name', ''), Res.get('Price', 0), Res.get('PriceOld', 0), Res.get('OnStock', 1), Res.get('Image', ''))

class TWebScraperSitemap(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrlRoot: str, aSleep: int):
        super().__init__(aParent, aScheme, aSleep)

        self.UrlRoot = aUrlRoot

    async def LoadSiteMap(self, aUrl: str) -> list:
        Res = []

        Info = await self.Download.Get(aUrl)
        if (Info):
            Data, Status = Info
            if (Status == 200):
                if (aUrl.endswith('.xml.gz')):
                    Data = gzip.decompress(Data)

                Urls = re.findall('<loc>(.*?)</loc>', Data.decode())
                for Url in Urls:
                    if (Url.endswith('.xml')) or (Url.endswith('.xml.gz')):
                        Res += await self.LoadSiteMap(Url)
                    else:
                        Res.append(Url.strip('/'))
        return Res

    async def _DoWorkerStart(self):
        SiteMap = await self.LoadSiteMap(self.UrlRoot + '/sitemap.xml')
        if (SiteMap):
            self.DblQueue.AddList('Url', SiteMap)  
        else:
            Log.Print(1, 'e', 'No sitemap %s' % (self.UrlRoot))

    async def _DoWorkerUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = BeautifulSoup(aData, 'lxml')
        Data = TScheme.ParseKeys(Soup, self.Scheme)

        Info = Data.get('Product')
        if (Info):
            Value, Keys, Err = Info
            Dif = set(Keys) - set(Value.keys())
            if (Dif):
                Log.Print(1, 'i', 'Missed %s in %s' % (Dif, aUrl))
            else:
                print('---x1', aUrl, Value)
                self.UrlScheme += 1
                Price = Value['Price'] 
                Value['Price'] = Price[0]
                Value['Currency'] = Price[1]
                await self.Sender.Add(Value)

class TWebScraperUpdate(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrls: list, aSleep: int):
        super().__init__(aParent, aScheme, aSleep)
        
        for Url in aUrls:
            self.Queue.put_nowait(Url)

    async def _DoWorkerUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = BeautifulSoup(aData, "lxml")

        Msg = 'status:%d, found:%2d, done:%d, total:%dM, %s ;' % (aStatus, self.TotalUrl, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)

