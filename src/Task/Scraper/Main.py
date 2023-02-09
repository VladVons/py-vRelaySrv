# Created: 2022.02.17
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from collections import deque
import asyncio
import random
#
from Inc.Db.DbList import TDbListSafe
from Inc.Util.Obj import DeepGet
from Inc.UtilP.DownloadSpeed import TDownloadSpeed
from Inc.UtilP.Misc import FilterKeyErr
from IncP.ApiWeb import TWebSockClient
from IncP.Log import Log
from IncP.Scheme.Scheme import TScheme
#
from .Api import Api
#from .Selenium import TStarter
from .WebScraper import TWebScraperFull, TWebScraperUpdate, TWebScraperSitemap


class TMain():
    def __init__(self, aConf: dict):
        self.Conf = aConf
        self.Scrapers = deque((), self.Conf.get('MaxTasks', 10))

        self.WebSock = TWebSockClient(aConf.SrvAuth)
        self.WebSock.OnMessage = self._OnWebSockMessage

    async def _DoPost(self, aOwner, aMsg):
        pass

    async def _OnWebSockMessage(self, aData: dict):
        print('--- _OnWebSockMessage', aData)

    async def _Worker(self, aTaskId: int):
        Log.Print(1, 'i', '_Worker(). Start Id %d' % (aTaskId))
        while (True):
            Wait = random.randint(2, 5)
            #Log.Print(1, 'i', '_Worker(). Ready for task. Id %d, wait %d sec' % (aTaskId, Wait))
            await asyncio.sleep(Wait)

            #await self.WebSock.Send({'data': 'Hellow from client. Id %s' % aTaskId})
            #continue

            DataApi = await Api.DefHandler('get_task')
            Data = DeepGet(DataApi, 'Data.Data')
            if (Data):
                Scheme = TScheme(Data['scheme'])
                Type = Data.get('type')
                if (Type == 'full'):
                    if (Data['sitemap']):
                        Scraper = TWebScraperSitemap(self, Scheme, Data['url'], Data['id'], Data['sleep'])
                    else:
                        Scraper = TWebScraperFull(self, Scheme, Data['url'], Data['id'], Data['sleep'])
                elif (Type == 'update'):
                    Scraper = TWebScraperUpdate(self, Scheme, Data['urls'], Data['sleep'])
                elif (Type == 'update_selenium'):
                    #await TStarter().ThreadCreate(Data['Urls'])
                    continue
                else:
                    Log.Print(1, 'e', '_Worker(). Unknown type: `%d`' % (Type))
                    return

                self.Scrapers.append(Scraper)
                await Scraper._Worker()

    async def _CreateTasks(self, aMaxTasks: int = 10):
        Tasks = [asyncio.create_task(self._Worker(i)) for i in range(aMaxTasks)]
        await asyncio.gather(*Tasks)

    def GetInfo(self) -> list:
        return [x.GetInfo() for x in self.Scrapers]

    async def GetMaxWorkers(self, aWorkers) -> int:
        Res = self.Conf.get('max_workers', aWorkers)
        if (not Res):
            Url = self.Conf.get('speed_test_url')
            if (Url):
                Speed = await TDownloadSpeed(2).Test(Url)
                Res = round(Speed / 5)
            else:
                Res = 5
        return Res

    async def Run(self):
        WaitLocalHost = 2
        await asyncio.sleep(WaitLocalHost)

        while (True):
            try:
                #TaskWS = asyncio.create_task(self.WebSock.Connect('ws/api', {'id': 1}))

                DataApi = await Api.GetUserConfig()
                Err = FilterKeyErr(DataApi)
                if (Err):
                    Log.Print(1, 'e', 'Run() %s' % Err)
                else:
                    Dbl = TDbListSafe().Import(DeepGet(DataApi, 'data.data'))
                    Conf = Dbl.ExportPair('name', 'data')
                    Workers = int(Conf.get('workers', 0))
                    MaxWorkers = await self.GetMaxWorkers(Workers)
                    await self._CreateTasks(MaxWorkers)
            except Exception as E:
                Log.Print(1, 'x', 'Run()', aE = E)
            await asyncio.sleep(30)
