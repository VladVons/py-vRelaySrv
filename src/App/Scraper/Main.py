'''
VladVons@gmail.com
2022.02.17
'''


import asyncio
import random
import json
from collections import deque
#
from App import ConfApp
from IncP.Log import Log
from IncP.DB.Scraper_pg import TDbApp
from .WebScraper import TWebScraperDb


class TMain():
    def __init__(self, aConf: dict):
        self.Conf = aConf
        self.Scrapers = deque((), self.Conf.get('MaxTasks', 10))

    async def _DoPost(self, aOwner, aMsg):
        pass

    async def _Worker(self, aTaskId: int):
        while (True):
            Wait = random.randint(1, 5)
            Log.Print(1, 'i', '_Worker()' , 'Ready for task. Id %d, wait %d' % (aTaskId, Wait))
            await asyncio.sleep(Wait)

            Rows = await self.Db.GetFreeTask()
            if (Rows):
                Row = Rows[0]
                try:
                    json.loads(Row['scheme'].strip())
                except json.decoder.JSONDecodeError as E:
                    Log.Print(1, 'x', '_Worker()', E)
                    continue

                Row['tasks'] = 4
                Row['sleep'] = 3
                #await self.Db.UpdateFreeTask(Row['id'])
                #Row['url'] = 'https://largo.com.ua'
                #Row['url'] = 'https://brain.com.ua/ukr'
                Row['url'] = 'https://compx.com.ua'
                #Row['url'] = 'https://hard.rozetka.com.ua'
                Scraper = TWebScraperDb(self, Row['url'], Row['tasks'], Row['sleep'], json.loads(Row['scheme']))
                self.Scrapers.append(Scraper)
                await Scraper.Run()

    async def _CreateTasks(self):
        MaxTasks = self.Conf.get('MaxTasks', 10)
        Tasks = [asyncio.create_task(self._Worker(i)) for i in range(MaxTasks)]
        await asyncio.gather(*Tasks)

    def GetInfo(self) -> list:
        return [i.GetInfo() for i in self.Scrapers]

    async def Run(self):
        self.Db = TDbApp(ConfApp.AuthDb)
        await self.Db.Connect()
        await self.Db.ExecFile('IncP/DB/vHttpScraper.pg.sql')
        await self._CreateTasks()
        await self.Db.Close()
