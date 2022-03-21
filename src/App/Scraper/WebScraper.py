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

UrlChekIP = 'http://icanhazip.com'

class TWebScraper():
    def __init__(self, aParent, aUrlRoot: str, aMaxTasks: int = 8, aSleep: int = 1):
        self.UrlRoot = aUrlRoot
        self.MaxTasks = aMaxTasks
        self.Sleep = aSleep
        self.Parent = aParent

        self.Url = []
        self.UrlCnt = 0
        self.TotalData = 0
        self.IsRun = False

        self.Download = TDownload(self.Parent.Conf.get('Proxy', []))

        self.Queue = asyncio.Queue()
        #self.Queue.put_nowait(UrlChekIP)
        self.Queue.put_nowait(aUrlRoot)

        self.Event = asyncio.Event()
        self.Wait(False)

    async def _DoGrab(self, aUrl: str, aSoup, aStatus: int, aTaskId: int):
        raise NotImplementedError()

    @staticmethod
    def IsMimeApp(aUrl: str) -> bool:
        Path = urlparse(aUrl).path
        Ext = os.path.splitext(Path)[1]
        return Ext in ['.zip', '.rar', '.xml', '.pdf', '.jpg', '.jpeg', '.png', '.gif']

    async def _GrabHref(self, aUrl: str, aData: str, aStatus: int, aTaskId: int):
        self.TotalData += len(aData)
        self.UrlCnt += 1

        Soup = BeautifulSoup(aData, "lxml")
        for A in Soup.find_all("a"):
            Href = A.get("href", '').strip().rstrip('/')
            if (Href):
                Path = urlparse(Href).path
                Ext = os.path.splitext(Path)[1]

                if (Href.startswith('/')):
                    Href = self.UrlRoot + Href

                if (Href.startswith(self.UrlRoot)) and \
                   (not Href.startswith('#')) and \
                   (not Href in self.Url) and \
                   (not self.IsMimeApp(Href)):
                    self.Url.append(Href)
                    self.Queue.put_nowait(Href)
                    #Log.Print(1, 'i', '_GrabHref()', 'Add url %s' % (Href))
        await self._DoGrab(aUrl, Soup, aStatus, aTaskId)

    async def _Worker(self, aTaskId: int):
        await asyncio.sleep(aTaskId)
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
                        await self._GrabHref(Url, Data, Status, aTaskId)
            except (aiohttp.ClientConnectorError, aiohttp.ClientError) as E:
                Log.Print(1, 'x', '_Worker()', E, Url)
            except asyncio.TimeoutError as E:
                Log.Print(1, x, '_Worker()', E, Url)
            finally:
                self.Queue.task_done()
        Log.Print(1, 'i', '_Worker()', '%d done' % (aTaskId))

    def GetInfo(self) -> dict:
        return {'UrlRoot': self.UrlRoot, 'UrlCnt': self.UrlCnt, 'UrlFound': len(self.Url), 'TotalData': self.TotalData, 'Sleep': self.Sleep, 'MaxTasks': self.MaxTasks}

    def Wait(self, aEnable: bool):
        if  (aEnable):
            self.Event.clear()
        else:
            self.Event.set()

    def Stop(self):
        self.Wait(False)
        self.IsRun = False
        if (self.Queue.empty()):
            for Task in self.Tasks():
                Task.cancel()
            self.Tasks = []

    async def Run(self):
        self.Tasks = [asyncio.create_task(self._Worker(i)) for i in range(self.MaxTasks)]
        Log.Print(1, 'i', 'Parse()', 'URL:%s, Tasks:%d(%d)' % (self.UrlRoot, self.MaxTasks, len(asyncio.all_tasks())))
        await asyncio.gather(*self.Tasks)
        self.IsRun = False
        Log.Print(1, 'i', 'Parse()', 'Done')


class TWebScraperDb(TWebScraper):
    def __init__(self, aParent, aUrlRoot: str, aMaxTasks: int, aSleep: int, aScheme: dict):
        super().__init__(aParent, aUrlRoot, aMaxTasks, aSleep)
        self.Scheme = aScheme
        self.UrlScheme = 0

    async def _DoGrab(self, aUrl: str, aSoup, aStatus: int, aTaskId: int):
        Msg = 'task:%2d, status:%d, found:%2d, done:%d, total:%dM, %s ;' % (aTaskId, aStatus, len(self.Url), self.UrlCnt, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)

        Res = TScheme.Parse(aSoup, self.Scheme)
        if (Res):
            self.UrlScheme += 1
            #print('---x1', Res)
            #await self.Parent.Db.InsertUrl(aUrl, Res.get('Name', ''), Res.get('Price', 0), Res.get('PriceOld', 0), Res.get('OnStock', 1), Res.get('Image', ''))
