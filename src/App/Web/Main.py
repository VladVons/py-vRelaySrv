'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:.

https://github.com/aio-libs/aiohttp
https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners
'''

import asyncio
import json
from aiohttp import web
#
from IncP.Log  import Log
from Inc.Plugin import Plugin
from IncP.DB.Scraper_pg import TDbApp
from .Api import TApi


class TWeb():
    def __init__(self, aConf: dict):
        self.Conf = aConf
        self.Db = TDbApp(aConf.DbAuth)
        self.Api = TApi(self)

    async def _rIndex(self, aRequest: web.Request) -> web.Response:
        Text = "TWeb._rIndex() %03d" % (self.Cnt)
        return web.Response(text=Text)

    async def _rApi(self, aRequest: web.Request) -> web.Response:
        Name = aRequest.match_info.get('Name')
        Post = aRequest.text
        Res = await self.Api.Call(Name, Post)
        return web.json_response(Res)
 
    async def Run(self):
        await self.Db.Connect()
        await self.Db.ExecFile('IncP/DB/Scraper_pg.sql')

        App = web.Application()
        App.add_routes([
            web.get("/", self._rIndex),
            web.get('/api/{Name:.*}', self._rApi),
            web.post('/api/{Name:.*}', self._rApi)
        ])

        #Runner = web.AppRunner(App)
        #await Runner.setup()
        #Site = web.TCPSite(Runner, '0.0.0.0', self.Conf.get('Port', 8080))
        #await Site.start()

        try:
            await web._run_app(App, host = '0.0.0.0', port = self.Conf.get('Port', 8080), shutdown_timeout = 60.0,  keepalive_timeout = 75.0)
        finally:
            await self.Db.Close()
