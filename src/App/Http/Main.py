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
from Inc.Log  import Log


async def handler(request: web.Request) -> web.Response:
    return web.Response(text="Hello world")


class THttp():
    async def Run(self):
        App = web.Application()
        App.add_routes([web.get("/", handler)])

        Runner = web.AppRunner(App)
        await Runner.setup()
        Site = web.TCPSite(Runner, 'localhost', 8080)
        await Site.start()
