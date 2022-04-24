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
from .WebScraper import TWebScraperFull, TWebScraperUpdate, TWebScraperSitemap
from .Selenium import TStarter
from .Api import Api


class TMain():
    def __init__(self, aConf: dict):
        self.Conf = aConf
        self.Scrapers = deque((), self.Conf.get('MaxTasks', 10))

    async def _DoPost(self, aOwner, aMsg):
        pass

    async def _Worker(self, aTaskId: int):
        while (True):
            Wait = random.randint(2, 5)
            #Log.Print(1, 'i', '_Worker(). Ready for task. Id %d, wait %d sec' % (aTaskId, Wait))
            await asyncio.sleep(Wait)

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

    async def cbWebSock(self, aData):
        print('--x', aData)
        pass

    async def WebSock(self):
        Auth = self.Conf.SrvAuth
        Url = 'http://%s:%s/%s/api' % (Auth.get('Server'), Auth.get('Port'), Auth.get('WebSock'))
        async with aiohttp.ClientSession() as Session:
            async with Session.ws_connect(Url) as WS:
                await WS.send_str('123')

                async for Msg in WS:
                    if (Msg.type == aiohttp.WSMsgType.TEXT):
                        await self.cbWebSock(Msg.data)
                    elif (Msg.type == aiohttp.WSMsgType.CLOSED) or (Msg.type == aiohttp.WSMsgType.ERROR):
                        break

    async def Run(self):
        WaitLocalHost = 1
        await asyncio.sleep(WaitLocalHost)

        while (True):
            try:
                WebSock = self.WebSock()
                asyncio.create_task(WebSock)

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
                WebSock.cancel()
            await asyncio.sleep(30)
