'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.17
License:     GNU, see LICENSE for more details
Description:
'''


import asyncio
import random
import aiohttp
from collections import deque
#
from IncP.Log import Log
from IncP.ApiWeb import TWebSockClient
from .WebScraper import TWebScraperFull, TWebScraperUpdate, TWebScraperSitemap
from .Selenium import TStarter
from .Api import Api


class TMain():
    def __init__(self, aConf: dict):
        self.Conf = aConf
        self.Scrapers = deque((), self.Conf.get('MaxTasks', 10))

        self.WebSock = TWebSockClient(aConf.SrvAuth)
        self.WebSock.OnMessage = self._OnWebSockMessage

    async def _DoPost(self, aOwner, aMsg):
        pass

    async def _OnWebSockMessage(self, aData: dict):
        print(aData)

    async def _Worker(self, aTaskId: int):
        while (True):
            Wait = random.randint(2, 5)
            #Log.Print(1, 'i', '_Worker(). Ready for task. Id %d, wait %d sec' % (aTaskId, Wait))
            await asyncio.sleep(Wait)

            #await self.WebSock.Send({'Data': 'Hellow from client. Id %s' % aTaskId})
            continue

            DataA = await Api.GetTask()
            Data = DataA.get('Data', {}).get('Data')
            if (Data):
                Type = Data.get('Type')
                if (Type == 'Full'):
                    if (Data['site.sitemap']):
                        Scraper = TWebScraperSitemap(self, Data['site.scheme'], Data['site.url'], Data['site.sleep'])
                    else:
                        Scraper = TWebScraperFull(self, Data['site.scheme'], Data['site.url'], Data['site.sleep'])
                elif (Type == 'Update'):
                    Scraper = TWebScraperUpdate(self, Data['site.scheme'], Data['Urls'], Data['site.sleep'])
                elif (Type == 'UpdateSelenium'):
                    await TStarter().ThreadCreate(Data['Urls'])
                    continue
                else:
                    Log.Print(1, 'e', '_Worker(). Unknown type: %d' % (Type))
                    return

                self.Scrapers.append(Scraper)
                await Scraper._Worker()

    async def _CreateTasks(self, aMaxTasks: int = 10):
        Tasks = [asyncio.create_task(self._Worker(i)) for i in range(aMaxTasks)]
        await asyncio.gather(*Tasks)

    def GetInfo(self) -> list:
        return [x.GetInfo() for x in self.Scrapers]

    async def Run(self):
        WaitLocalHost = 1
        await asyncio.sleep(WaitLocalHost)

        while (True):
            try:
                TaskWS = asyncio.create_task(self.WebSock.Connect('ws/api', {'id': 1}))

                DataA = await Api.GetConfig()
                Data = DataA.get('Data', {}).get('Data')
                if (Data):
                    MaxWorkers = Data.get('MaxWorkers', self.Conf.get('MaxWorkers', 5))
                    await self._CreateTasks(MaxWorkers)
                else:
                    Log.Print(1, 'i', 'Run(). Cant get config from server')
            except Exception as E:
                Log.Print(1, 'x', 'Run()', aE = E)
            finally:
                TaskWS.cancel()
            await asyncio.sleep(30)
