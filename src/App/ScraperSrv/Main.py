'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.16
License:     GNU, see LICENSE for more details
Description:
'''

import base64
from aiohttp import web
#
from IncP.DB.Scraper_pg import TDbApp
from .Api import TApi


class TScraperSrv():
    def __init__(self, aConf: dict):
        self.Conf = aConf

    async def CheckAuth(self, aRequest: web.Request) -> bool:
        if (self.Conf.get('Auth')):
            Auth = aRequest.headers.get('Authorization')
            if (Auth):
                User, Passw = base64.b64decode(Auth.split()[1]).decode().split(':')
                DBL = await self.Api.Db.Login(User, Passw)
                return DBL.GetSize() > 0
        else:
            return True

    async def _rIndex(self, aRequest: web.Request) -> web.Response:
        if (await self.CheckAuth(aRequest)):
            Name = aRequest.match_info.get('Name')
            Post = await aRequest.text()
            Res = await self.Api.Call(Name, Post)
            return web.json_response(Res)
        else:
            Res = {'Error': 'Authorization'}
            return web.json_response(Res, status=403)
 
    async def Run(self):
        self.Api = TApi()
        await self.Api.DbInit(self.Conf.DbAuth)

        App = web.Application()
        App.add_routes([
            web.get('/{Name:.*}', self._rIndex),
            web.post('/{Name:.*}', self._rIndex)
        ])

        try:
            await web._run_app(App, host = '0.0.0.0', port = self.Conf.get('Port', 8081), shutdown_timeout = 60.0,  keepalive_timeout = 75.0)
        finally:
            await self.Api.Db.Close()
