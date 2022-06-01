'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.19
License:     GNU, see LICENSE for more details
'''


from aiohttp import web
from datetime import datetime
import asyncio
import json
#
from Inc.DB.DbList import TDbList
from IncP.ApiWeb import TApiBase
from IncP.DB.Db import TDbSql
from IncP.DB.Scraper_pg import TDbApp
from IncP.Log import Log, TEchoDb


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
    def __init__(self):
        super().__init__()

        self.Url = {
            'get_hand_shake':       {'param': []},
            'get_task':             {'param': []},
            'get_scheme_empty':     {'param': ['cnt']},
            'get_scheme_not_empty': {'param': ['cnt']},
            'get_scheme':           {'param': ['id']},
            'get_sites':            {'param': ['*']},
            'get_user_id':          {'param': ['login', 'passw']},
            'get_user_config':      {'param': ['id']},
            'add_sites':            {'param': ['dbl']},
            'send_result':          {'param': ['*']},
            'set_scheme':           {'param': ['id', 'scheme']}
        }

        self.Db: TDbApp = None
        self.ApiTask = TApiTask(self)

    async def DoAuthRequest(self, aUser: str, aPassw: str):
        Dbl = await self.Db.AuthUser(aUser, aPassw)
        return (not Dbl.IsEmpty())

    async def path_get_hand_shake(self, aPath: str, aData: dict) -> dict:
        return True

    async def path_get_task(self, aPath: str, aData: dict) -> dict:
        return await self.ApiTask.Get(aData)

    async def path_get_user_config(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetUserConfig(aData.get('id'))
        return Dbl.Export()

    async def path_get_scheme_empty(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetScheme(True, aData.get('cnt', 1))
        return Dbl.Export()

    async def path_get_scheme_not_empty(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetScheme(False, aData.get('cnt', 1))
        return Dbl.Export()

    async def path_get_scheme(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetSiteById(aData.get('id'))
        return Dbl.Export()

    async def path_set_scheme(self, aPath: str, aData: dict) -> dict:
        return await self.Db.SetScheme(aData.get('id'), aData.get('scheme'))

    async def path_get_sites(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.GetSites(aData.get('cnt', -1))
        return Dbl.Export()

    async def path_get_user_id(self, aPath: str, aData: dict) -> dict:
        Dbl = await self.Db.AuthUser(aData.get('login'), aData.get('passw'))
        if (not Dbl.IsEmpty()):
            return Dbl.Rec.GetField('id')

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


Api = TApi()
