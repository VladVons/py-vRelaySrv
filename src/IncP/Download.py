"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.10
License:     GNU, see LICENSE for more details
Description:
"""

import time
import random
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
#
from IncP.Log import Log

#from fake_useragent import UserAgent
#self.ua = UserAgent()
#ua.random


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
    def __init__(self, aProxies: list = [], aHeaders: THeaders = None, aAuth: tuple = ()):
        self.Proxies = aProxies
        self.Headers = aHeaders
        self.Auth = aAuth

    async def _GetWithSem(self, aUrl: str, aSem: asyncio.Semaphore) -> dict:
        async with aSem:
            return await self.Get(aUrl)

    async def Get(self, aUrl: str) -> dict:
        TimeAt = time.time()
        try:
            async with aiohttp.ClientSession(connector=self._GetConnector(), auth=self._GetAuth()) as Session:
                async with Session.get(aUrl, headers=self._GetHeaders()) as Response:
                    Data = await Response.read()
                    Res = {'Data': Data, 'Status': Response.status, 'Time': time.time() - TimeAt}
        except (aiohttp.ClientConnectorError, aiohttp.ClientError, aiohttp.InvalidURL) as E:
                    ErrMsg = Log.Print(1, 'x', 'Download.Get(). %s' % (aUrl), aE = E)
                    Res = {'Err': E, 'Msg': ErrMsg}
        return Res

    async def Gets(self, aUrls: list, aMaxConn: int = 5) -> list:
        Sem = asyncio.Semaphore(aMaxConn)
        Tasks = [asyncio.create_task(self._GetWithSem(Url, Sem)) for Url in aUrls]
        return await asyncio.gather(*Tasks)

    def _GetConnector(self) -> ProxyConnector:
        if (self.Proxies):
            return ProxyConnector.from_url(random.choice(self.Proxies))

    def _GetHeaders(self) -> THeaders:
        if (self.Headers):
            return self.Headers.Get()

    def _GetAuth(self) -> aiohttp.BasicAuth:
        if (self.Auth):
            return aiohttp.BasicAuth(login=self.Auth[0], password=self.Auth[1])
