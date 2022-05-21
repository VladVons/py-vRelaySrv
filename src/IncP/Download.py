'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.10
License:     GNU, see LICENSE for more details
'''

import time
import random
import asyncio
import aiohttp
import socket
from urllib.parse import urlparse
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup

#
from IncP.Log import Log

#from fake_useragent import UserAgent
#self.ua = UserAgent()
#ua.random


def CheckHost(aUrl: str) -> bool:
    Host = urlparse(aUrl).hostname
    return socket.gethostbyname(Host)

async def GetUrlSoup(aUrl: str) -> BeautifulSoup:
    Download = TDownload(aHeaders = THeaders())
    UrlDown = await Download.Get(aUrl, True)
    if (UrlDown['Status'] == 200) and (UrlDown.get('Type') != 'Err'):
        Data = UrlDown['Data']
        Res = BeautifulSoup(Data, 'lxml')
        if (len(Res) == 0):
            Res = BeautifulSoup(Data, 'html.parser')
        return Res


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
            'User-Agent': 'Mozilla/5.0 (%s) %s' % (random.choice(self.OS), random.choice(self.Browser)),
            'Accept-Language': 'uk-UA,uk;'
        }


class TDownload():
    def __init__(self, aProxies: list = [], aHeaders: THeaders = None, aAuth: tuple = ()):
        self.Proxies = aProxies
        self.Headers = aHeaders
        self.Auth = aAuth
        self.Timeout = 10
        self.OnGet = None
        self.FakeRead = False

    async def _GetWithSem(self, aUrl: str, aSem: asyncio.Semaphore) -> dict:
        async with aSem:
            Res = await self.Get(aUrl)
            Res['Url'] = aUrl
            return Res

    async def Get(self, aUrl: str, aDecode: bool = False) -> dict:
        TimeAt = time.time()
        try:
            async with aiohttp.ClientSession(connector=self._GetConnector(), auth=self._GetAuth()) as Session:
                async with Session.get(aUrl, headers=self._GetHeaders(), timeout=self.Timeout) as Response:
                    if (self.FakeRead):
                        Data = await Response.content.read(0)
                    else:
                        Data = await Response.read()
                        if (Data) and (aDecode):
                            Data = Data.decode(errors='ignore')
                    Res = {'Data': Data, 'Status': Response.status, 'Time': time.time() - TimeAt}
        except (aiohttp.ClientConnectorError, aiohttp.ClientError, aiohttp.InvalidURL, asyncio.TimeoutError) as E:
                    ErrMsg = Log.Print(1, 'x', 'Download.Get(). %s' % (aUrl), aE = E)
                    Res = {'Type': 'Err', 'Data': E, 'Msg': ErrMsg, 'Status': -1}

        if (self.OnGet):
            await self.OnGet(aUrl, Res)
            await asyncio.sleep(0.1)

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
