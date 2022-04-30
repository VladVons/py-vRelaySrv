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
from IncP.DB.Db import TDbSql
from IncP.ApiWeb import TApiBase


class TApiTask():
    def __init__(self, aParent: 'TApi'):
        self.Parent = aParent
        self.Tasks = TDbList( [('SiteId', int), ('StartAt', type(datetime.now())), ('Urls', TDbSql)] )
        self.Lock = asyncio.Lock()

    async def Get(self, aData: dict) -> dict:
        async with self.Lock:
            ExclId = self.Tasks.ExportList('SiteId')

            Dbl = await self.Parent.Db.GetSitesForUpdateFull(aExclId=ExclId, aUpdDaysX=2)
            if (not Dbl.IsEmpty()):
                Dbl.Tag = 'Full'
                Dbl.Shuffle()
                Res = Dbl.Rec.GetAsDict()
                Res['Type'] = Dbl.Tag
                Res['scheme'] = json.loads(Res['scheme'])
                self.Tasks.RecAdd([Dbl.Rec.GetField('id'), datetime.now(), Dbl])
                return Res
            else:
                Dbl = await self.Parent.Db.GetSitesForUpdate(aExclId=ExclId)
                if (not Dbl.IsEmpty()):
                    Dbl.Shuffle()
                    SiteId = Dbl.Rec.GetField('id')
                    Res = Dbl.Rec.GetAsDict()

                    Dbl = await self.Parent.Db.GetSiteUrlsForUpdate(SiteId)
                    Dbl.Tag = 'Update'
                    Res['Type'] = Dbl.Tag
                    Res['Urls'] = Dbl.GetData()

                    self.Tasks.RecAdd([SiteId, datetime.now(), Dbl])
                    return Res


class TApi(TApiBase):
    Url = {
        'get_task':             {'param': []},
        'get_config':           {'param': ['user']},
        'get_scheme_empty':     {'param': []},
        'get_scheme_by_id':     {'param': ['id']},
        'get_sites':            {'param': ['*']},
        'add_sites':            {'param': ['dbl']},
        'send_result':          {'param': ['*']}
    }

    def __init__(self):
        self.Db: TDbApp = None
        self.ApiTask = TApiTask(self)

    async def path_get_task(self, aPath: str, aData: dict) -> dict:
        return await self.ApiTask.Get(aData)

    async def path_get_config(self, aPath: str, aData: dict) -> dict:
        DBL = await self.Db.GetConfig(aData.get('user'))
        return DBL.Rec.GetAsDict()

    async def path_get_scheme_empty(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetSchemeEmpty()
        if (not Dbl.IsEmpty()):
            Dbl.Shuffle()
            return Dbl.Rec.GetAsDict()

    async def path_get_scheme_by_id(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetSiteById(aData.get('id'))
        return Dbl.Rec.GetAsDict()

    async def path_get_sites(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetSites()
        return Dbl.Export()

    async def path_add_sites(self, aPath: str, aData: dict) -> dict:
        Data = aData.get('dbl')
        Dbl = TDbSql(self.Db).Import(Data)
        await Dbl.Insert('site')
        return True

    async def path_send_result(self, aPath: str, aData: dict) -> dict:
        return True

    async def DbInit(self, aAuth: dict):
        self.Db = TDbApp(aAuth)
        await self.Db.Connect()
        # await self.Db.ExecFile('IncP/DB/Scraper_pg.sql')

        Dbl = await self.Db.GetDbVersion()
        Rec = Dbl.Rec
        Version = Rec.GetField('version').split()[:2]
        Uptime = Rec.GetField('uptime')
        Log.Print(1, 'i', 'Server: %s, Uptime: %sd%sh, DbName: %s, DbSize: %sM, Tables %s' %
            (' '.join(Version), Uptime.days, int(Uptime.seconds/3600), Rec.GetField('name'), round(Rec.GetField('size') / 1000000, 2), Rec.GetField('tables'))
        )

        Log.AddEcho(TEchoDb(self.Db))

    async def DbClose(self):
        List = Log.FindEcho(TEchoDb.__name__)
        Log.Echoes.remove(List[0])
        await self.Db.Close()
