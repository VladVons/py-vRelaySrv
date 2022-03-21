'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.16
License:     GNU, see LICENSE for more details
Description:
'''


from aiohttp import web
#
from IncP.DB.Scraper_pg import TDbApp
from .Api import TApi


class TScraperSrv():
    def __init__(self, aConf: dict):
        self.Conf = aConf

    async def _rIndex(self, aRequest: web.Request) -> web.Response:
        Name = aRequest.match_info.get('Name')
        Post = aRequest.text
        Res = await self.Api.Call(Name, Post)
        return web.json_response(Res)
 
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
