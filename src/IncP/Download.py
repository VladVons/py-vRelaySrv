"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.10
License:     GNU, see LICENSE for more details
Description:
"""


import random
import aiohttp
from aiohttp_socks import ProxyConnector


class THeaders():
    def __init__(self):
        self.OS = [
            'Macintosh; Intel Mac OS X 10_15_5', 
            'Windows NT 10.0; Win64; x64; rv:77', 
            'Linux; Intel Ubuntu 20.04'
        ]
        self.Browser = [
            'Chrome/83', 
            'Firefox/77', 
            'Opera/45'
        ]

    def Get(self):
        return  {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (%s) %s' % (random.choice(self.OS), random.choice(self.Browser))
        }


class TDownload():
    def __init__(self, aProxies: list = []):
        self.Proxies = aProxies
        self.Headers = THeaders()

    async def Get(self, aUrl: str) -> tuple:
        async with aiohttp.ClientSession(connector=self._GetConnector()) as Session:
            async with Session.get(aUrl, headers=self.Headers.Get()) as Response:
                Data = await Response.read()
                return (Data, Response.status)

    def _GetConnector(self) -> ProxyConnector:
        if (self.Proxies):
            return ProxyConnector.from_url(random.choice(self.Proxies))
