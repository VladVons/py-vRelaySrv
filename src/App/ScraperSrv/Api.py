'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.19
License:     GNU, see LICENSE for more details
Description:
'''


import json
import random
import asyncio
from datetime import datetime
#
from IncP.Log import Log, TEchoDb
from IncP.DB.Scraper_pg import TDbApp
from Inc.DB.DbList import TDbList


class TApiTask():
    def __init__(self, aParent: 'TApi'):
        self.Parent = aParent
        self.Tasks = TDbList([], ['SiteId', 'StartAt', 'Urls'])
        self.Lock = asyncio.Lock()

    async def Get(self, aData: dict) -> dict:
        async with self.Lock:
            ExclId = self.Tasks.GetList('SiteId')

            DblUpdFull = await self.Parent.Db.GetSitesForUpdateFull(aExclId = ExclId, aUpdDaysX = 2)
            if (DblUpdFull.GetSize() > 0):
                DblUpdFull.Shuffle()
                SiteId = DblUpdFull.Rec.GetField('site.id')
                Res = DblUpdFull.Rec.GetAsDict()

                self.Tasks.RecAdd([SiteId, datetime.now(), DblUpdFull])
                return Res
            else:
                DblUpd = await self.Parent.Db.GetSitesForUpdate(aExclId = ExclId)
                if (DblUpd.GetSize() > 0):
                    DblUpd.Shuffle()
                    SiteId = DblUpd.Rec.GetField('site.id')
                    DblUpdUrls = await self.Parent.Db.GetSiteUrlsForUpdate(SiteId)
                    Res = DblUpd.Rec.GetAsDict()
                    Res.update(DblUpdUrls.GetData())

                    self.Tasks.RecAdd([SiteId, datetime.now(), DblUpdUrls])
                    return Res


class TApi():
    Url = {
        'get_task':     {'param': []},
        'get_config':   {'param': ['user']}
    }

    def __init__(self):
        self.Db: TDbApp = None
        self.Cnt: int = 0

        self.ApiTask = TApiTask(self)

    @staticmethod
    def GetMethodName(aPath: str) -> str:
        return 'path_' + aPath.replace('/', '_')

    @staticmethod
    def CheckParam(aParam: dict, aPattern: list):
        Diff = set(aPattern) - set(aParam)
        if (Diff):
            return 'param not set. %s' % Diff

        Diff = set(aParam) - set(aPattern)
        if (Diff):
            return 'param unknown. %s' % Diff
 
    #@staticmethod
    #def GetRandStr(aLen: int, aPattern = 'YourPattern') -> str:
    #    return ''.join((random.choice(aPattern)) for x in range(aLen))

    async def Call(self, aPath: str, aParam: str) -> dict:
        UrlInf = self.Url.get(aPath)
        if (UrlInf):
            MethodName = self.GetMethodName(aPath)
            Method = getattr(self, MethodName, None)
            if (Method):
                ParamInf = UrlInf.get('param')
                if (ParamInf):
                    Param = json.loads(aParam)
                else:
                    Param = {}

                ErrMsg = self.CheckParam(Param, ParamInf)
                if (ErrMsg):
                    Log.Print(1, 'e', ErrMsg)
                    Res = {'Err': ErrMsg}
                else:
                    try:
                        Data = await Method(Param)
                        self.Cnt += 1
                    except Exception as E:
                        Data = None
                        Log.Print(1, 'x', 'Call()', aE = E)
                    Res = {'Data': Data}
            else:
                Res = {'Err': 'unknown method %s' % (MethodName)}
        else:
            Res = {'Err': 'unknown url %s' % (aPath)}
        return Res

    async def path_get_task(self, aData: dict) -> dict:
        return await self.ApiTask.Get(aData)

    async def path_get_config(self, aData: dict) -> dict:
        DBL = await self.Db.GetScraper(aData.get('user'))
        return DBL.GetData()

    async def DbInit(self, aAuth):
        self.Db = TDbApp(aAuth)
        await self.Db.Connect()
        #await self.Db.ExecFile('IncP/DB/Scraper_pg.sql')

        Log.AddEcho(TEchoDb(self.Db))
