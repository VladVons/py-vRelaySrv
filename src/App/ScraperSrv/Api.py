'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.19
License:     GNU, see LICENSE for more details
Description:
'''


import json
import asyncio
from datetime import datetime
#
from IncP.Log import Log, TEchoDb
from IncP.DB.Scraper_pg import TDbApp
from Inc.DB.DbList import TDbList
from IncP.DB.Db import TDbFetch


class TApiTask():
    def __init__(self, aParent: 'TApi'):
        self.Parent = aParent
        self.Tasks = TDbList( [('SiteId', int), ('StartAt', type(datetime.now())), ('Urls', TDbFetch)] )
        self.Lock = asyncio.Lock()

    async def Get(self, aData: dict) -> dict:
        async with self.Lock:
            ExclId = self.Tasks.GetList('SiteId')

            DblUpdFull = await self.Parent.Db.GetSitesForUpdateFull(aExclId=ExclId, aUpdDaysX=2)
            if (not DblUpdFull.IsEmpty()):
                DblUpdFull.Tag = 'Full'
                Res = {'Type': DblUpdFull.Tag}
                DblUpdFull.Shuffle()
                SiteId = DblUpdFull.Rec.GetField('site.id')
                Res.update(DblUpdFull.Rec.GetAsDict())
                Res['site.scheme'] = json.loads(Res['site.scheme'])
                self.Tasks.RecAdd([SiteId, datetime.now(), DblUpdFull])
                return Res
            else:
                DblUpd = await self.Parent.Db.GetSitesForUpdate(aExclId=ExclId)
                if (not DblUpd.IsEmpty()):
                    DblUpd.Shuffle()
                    SiteId = DblUpd.Rec.GetField('site.id')

                    DblUpdUrls = await self.Parent.Db.GetSiteUrlsForUpdate(SiteId)
                    DblUpdUrls.Tag = 'Update'
                    Res = {'Type': DblUpdUrls.Tag}
                    Res.update(DblUpd.Rec.GetAsDict())
                    Res['Urls'] = DblUpdUrls.GetData()

                    self.Tasks.RecAdd([SiteId, datetime.now(), DblUpdUrls])
                    return Res


class TApi():
    Url = {
        'get_task':             {'param': []},
        'get_config':           {'param': ['user']},
        'get_empty_scheme':     {'param': []},
        'get_sites':            {'param': []},
        'send_result':          {'param': ['*']}
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

    # @staticmethod
    # def GetRandStr(aLen: int, aPattern = 'YourPattern') -> str:
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

                if (ParamInf) and (ParamInf[0] == '*'):
                    ParamInf = Param.keys()

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
                        Log.Print(1, 'x', 'Call()', aE=E)
                    Res = {'Data': Data}
                    Res['Dbl'] = TDbList()
                    Res['Set'] = set([1,2,3])
            else:
                Res = {'Err': 'unknown method %s' % (MethodName)}
        else:
            Res = {'Err': 'unknown url %s' % (aPath)}
        return Res

    async def path_get_task(self, aData: dict) -> dict:
        return await self.ApiTask.Get(aData)

    async def path_get_config(self, aData: dict) -> dict:
        DBL = await self.Db.GetConfig(aData.get('user'))
        return DBL.Rec.GetAsDict()

    async def path_get_empty_scheme(self, aData: dict) -> dict:
        Dbl = await self.Db.GetEmptyScheme()
        if (not Dbl.IsEmpty()):
            Dbl.Shuffle()
            return Dbl.Rec.GetAsDict()

    async def path_get_sites(self, aData: dict) -> dict:
        Dbl = await self.Db.GetSites()
        return Dbl.DataExport()

    async def path_send_result(self, aData: dict) -> dict:
        return True

    async def DbInit(self, aAuth):
        self.Db = TDbApp(aAuth)
        await self.Db.Connect()
        # await self.Db.ExecFile('IncP/DB/Scraper_pg.sql')

        Log.AddEcho(TEchoDb(self.Db))
