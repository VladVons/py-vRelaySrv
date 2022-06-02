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


from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import asyncio
import gzip
import os
import random
import re
#
from .Api import Api
from Inc.DB.DbList import TDbList
from IncP.Download import TDownload, GetSoup
from IncP.Log import Log
from IncP.Utils import FilterKeyErr


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
            ('MPN', str)
        ])

    async def Add(self, aData: dict):
        self.Dbl.RecAdd()
        self.Dbl.Rec.SetAsDict(aData)
        if (self.Dbl.GetSize() > self.MaxSize):
            await self.Flush()

    async def Flush(self):
        if (not self.Dbl.IsEmpty()):
            Data = self.Dbl.Export()
            SrvRes = await Api.DefHandler('send_result', Data)
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
        self.Download.Opt.update({'Decode': True})

        self.DblQueue = TDbList( [('Url', str)] )
        self.Sender = TSender(self)

        self.Event = asyncio.Event()
        self.Wait(False)

    async def _DoWorkerUrl(self, aUrl: str, aData, aStatus: int):
        raise NotImplementedError()

    async def _DoWorkerStart(self): ...
    async def _DoWorkerEnd(self): ...
    async def _DoWorkerException(self): ...

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

        self.IsRun = True
        while (self.IsRun) and (not self.DblQueue.IsEmpty()):
            await self.Event.wait()
            await asyncio.sleep(random.randint(int(self.Sleep / 2), self.Sleep))

            Rec = self.DblQueue.RecPop()
            Url = Rec.GetField('Url')
            UrlDown = await self.Download.Get(Url)
            Err = FilterKeyErr(UrlDown)
            if (Err):
                await self._DoWorkerException(Url, UrlDown.get('Data'))
            else:
                Data = UrlDown['Data']
                Status = UrlDown['Status']
                if (Status == 200):
                    self.TotalData += len(Data)
                    self.TotalUrl += 1
                await self._DoWorkerUrl(Url, Data, Status)

        await self.Sender.Flush()
        await self._DoWorkerEnd()
        Log.Print(1, 'i', '_Worker(). done')


class TWebScraperFull(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrlRoot: str, aSleep: int = 1):
        super().__init__(aParent, aScheme, aSleep)

        self.UrlRoot = aUrlRoot
        self.Url = []
        self.RobotFile: RobotFileParser = None
        self.DblQueue.RecAdd([aUrlRoot])

    @staticmethod
    def IsMimeApp(aUrl: str) -> bool:
        Path = urlparse(aUrl).path
        Ext = os.path.splitext(Path)[1]
        return Ext in ['.zip', '.rar', '.xml', '.pdf', '.jpg', '.jpeg', '.png', '.gif']

    async def InitRobotFile(self, aUrl: str):
        self.RobotFile = RobotFileParser()
        UrlDown = await self.Download.Get(aUrl)
        Err = FilterKeyErr(UrlDown)
        if (not Err) and (UrlDown['Status'] == 200):
            Data = UrlDown['Data'].decode().splitlines()
            self.RobotFile.parse(Data)
        else:
            self.RobotFile.allow_all = True

    async def _DoWorkerStart(self):
        await self.InitRobotFile(self.UrlRoot + '/robots.txt')

    async def _DoWorkerUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = GetSoup(aData)
        Htrefs = Soup.find_all('a')
        for A in Htrefs:
            Href = A.get('href', '').strip().rstrip('/')
            if (Href):
                if (Href.startswith('/')):
                    Href = self.UrlRoot + Href

                if (Href.startswith(self.UrlRoot)) and \
                   (not Href.startswith('#')) and \
                   (self.RobotFile.can_fetch('*', Href)) and \
                   (not Href in self.Url) and \
                   (not self.IsMimeApp(Href)):
                    self.Url.append(Href)
                    self.DblQueue.RecAdd([Href])
                    #Log.Print(1, 'i', '_GrabHref(). Add url %s' % (Href))
        await self._GrabHref(aUrl, Soup, aStatus)

    async def _GrabHref(self, aUrl: str, aSoup, aStatus: int):
        Msg = 'status:%d, found:%2d, done:%d, total:%dM, %s ;' % (
            aStatus, len(self.Url), self.TotalUrl, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)

        self.Scheme.Parse(aSoup)
        if (not self.Scheme.Err):
            self.UrlScheme += 1
            #print('---x1', Res)
            #await self.Parent.Db.InsertUrl(aUrl, Res.get('Name', ''), Res.get('Price', 0), Res.get('PriceOld', 0), Res.get('OnStock', 1), Res.get('Image', ''))


class TWebScraperSitemap(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrlRoot: str, aSleep: int):
        super().__init__(aParent, aScheme, aSleep)

        self.UrlRoot = aUrlRoot

    async def LoadSiteMap(self, aUrl: str) -> list:
        Res = []

        UrlDown = await self.Download.Get(aUrl)
        Err = FilterKeyErr(UrlDown)
        if (not Err):
            Data = UrlDown['Data']
            Status = UrlDown['Status']
            if (Status == 200):
                if (aUrl.endswith('.xml.gz')):
                    Data = gzip.decompress(Data)

                Urls = re.findall('<loc>(.*?)</loc>', Data)
                for Url in Urls:
                    if (Url.endswith('.xml')) or (Url.endswith('.xml.gz')):
                        Res += await self.LoadSiteMap(Url)
                    else:
                        Res.append(Url.rstrip('/'))
            else:
                Log.Print(1, 'e', 'Sitemap error %s, %s' % (Status, self.UrlRoot))
        return Res

    async def _DoWorkerStart(self):
        SiteMap = await self.LoadSiteMap(self.UrlRoot + '/sitemap.xml')
        if (SiteMap):
            self.DblQueue.ImportList('Url', SiteMap)
        else:
            Log.Print(1, 'i', 'No sitemap %s' % (self.UrlRoot))

    async def _DoWorkerUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = GetSoup(aData)
        self.Scheme.Parse(Soup)
        if (len(self.Scheme.Pipe) >= 3):
            if (self.Scheme.Err):
                Log.Print(1, 'i', '_DoWorkerUrl() %s' % aUrl, self.Scheme.Err)
            else:
                self.UrlScheme += 1
                self.Scheme.Pipe['Price'], self.Scheme.Pipe['Currency'] = self.Scheme.Pipe.get('Price', (0, ''))
                await self.Sender.Add(self.Scheme.Pipe)

class TWebScraperUpdate(TWebScraper):
    def __init__(self, aParent, aScheme: dict, aUrls: list, aSleep: int):
        super().__init__(aParent, aScheme, aSleep)

        for Url in aUrls:
            self.Queue.put_nowait(Url)

    async def _DoWorkerUrl(self, aUrl: str, aData: str, aStatus: int):
        Soup = GetSoup(aData)
        Msg = 'status:%d, found:%2d, done:%d, total:%dM, %s ;' % (
            aStatus, self.TotalUrl, self.TotalData / 1000000, aUrl)
        Log.Print(1, 'i', Msg)

