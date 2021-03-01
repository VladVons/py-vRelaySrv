'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:.

https://github.com/aio-libs/aiohttp
https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners
'''

import asyncio
from aiohttp import web
#
from Inc.Conf import Conf
from IncP.Log  import Log
from Inc.Plugin import Plugin


class THttp():
    Cnt = 0

    async def Handler(self, request: web.Request) -> web.Response:
        self.Cnt += 1
        Text = "Handler: Hello world %03d" % self.Cnt
        print(Text)
        return web.Response(text=Text)

    async def Run(self):
        App = web.Application()
        App.add_routes([web.get("/", self.Handler)])

        Runner = web.AppRunner(App)
        await Runner.setup()
        Site = web.TCPSite(Runner, '0.0.0.0', Conf.get('Http_Port', 8080))
        await Site.start()
