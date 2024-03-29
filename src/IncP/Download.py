# Created: 2022.02.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import asyncio
import random
import socket
import time
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
from aiohttp_socks import ProxyConnector
#
from Inc.Misc.Misc import FilterKeyErr
from IncP.Log import Log

#from fake_useragent import UserAgent
#self.ua = UserAgent()
#ua.random


def CheckHost(aUrl: str) -> bool:
    Host = urlparse(aUrl).hostname
    return socket.gethostbyname(Host)

def GetSoup(aData: str) -> BeautifulSoup:
    Res = BeautifulSoup(aData, 'lxml')
    if (len(Res) == 0):
        Res = BeautifulSoup(aData, 'html.parser')
    return Res

async def GetSoupUrl(aUrl: str) -> BeautifulSoup:
    Download = TDownload()
    Download.Opt.update({'headers': TDHeaders(), 'decode': True})
    Res = await Download.Get(aUrl)
    Err = FilterKeyErr(Res)
    if (not Err):
        if (Res['status'] == 200):
            Soup = GetSoup(Res['data'])
            Res['soup'] = Soup
        else:
            Res['err'] = 'Status %s' % (Res['status'])
    return Res

class TDictDefCall(dict):
    def __getattr__(self, aName: str) -> object:
        Res = self.get(aName)
        if (hasattr(Res, 'Get')):
            Res = Res.Get()
        return Res


class TDHeaders():
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

    def Get(self) -> dict:
        return  {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (%s) %s' % (random.choice(self.OS), random.choice(self.Browser)),
            'Accept-Language': 'uk-UA,uk;'
        }


class TDAuth():
    def __init__(self, aUser: str, aPassw: str):
        self.User = aUser
        self.Passw = aPassw

    def Get(self) -> aiohttp.BasicAuth:
        return aiohttp.BasicAuth(login=self.User, password=self.Passw)


class TDConnector():
    def __init__(self):
        self.Proxies = []
        self.Mode = 0

    def Get(self) -> aiohttp.TCPConnector:
        if (self.Mode == 0):
            if (self.Proxies):
                return ProxyConnector.from_url(random.choice(self.Proxies))
        elif (self.Mode == 1):
            return aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)


class TDownload():
    def __init__(self):
        self.Opt = TDictDefCall({
            'connector': TDConnector(),
            'headers': None,
            'auth': None,
            'timeout': 10,
            'on_get': None,
            'fake_read': False,
            'decode': False
        })

    async def _GetWithSem(self, aUrl: str, aSem: asyncio.Semaphore) -> dict:
        async with aSem:
            Res = await self.Get(aUrl)
            Res['url'] = aUrl
            return Res

    async def _Get(self, aUrl: str) -> dict:
        TimeAt = time.time()
        try:
            async with aiohttp.ClientSession(connector=self.Opt.Connector, auth=self.Opt.Auth) as Session:
                async with Session.get(aUrl, headers=self.Opt.Headers, timeout=self.Opt.Timeout) as Response:
                    if (self.Opt.FakeRead):
                        Data = await Response.content.read(0)
                    else:
                        Data = await Response.read()
                        if (self.Opt.Decode):
                            Data = Data.decode(errors='ignore')
                    Res = {'data': Data, 'status': Response.status, 'time': round(time.time() - TimeAt, 2)}
        except (aiohttp.ClientConnectorError, aiohttp.ClientError, aiohttp.InvalidURL, asyncio.TimeoutError) as E:
            Log.Print(1, 'x', '_Get(). %s' % (aUrl), aE = E)
            Res = {'type': 'err', 'data': E, 'status': -1, 'time': round(time.time() - TimeAt, 2)}
        return Res

    async def Get(self, aUrl: str) -> dict:
        Res = await self._Get(aUrl)
        if (Res.get('type') == 'err'):
            await asyncio.sleep(1)
            E = Res.get('data')
            if (isinstance(E, aiohttp.ClientConnectorError)):
                Mode = self.Opt['connector'].Mode
                self.Opt['connector'].Mode = 1
                Res = await self._Get(aUrl)
                self.Opt['connector'].Mode = Mode
            elif (isinstance(E, aiohttp.ClientConnectorCertificateError)):
                pass
            else:
                Res = await self._Get(aUrl)

        if (self.Opt.OnGet):
            await self.Opt.OnGet(aUrl, Res)
            await asyncio.sleep(0.1)
        return Res

    async def Gets(self, aUrls: list, aMaxConn: int = 5) -> list:
        Sem = asyncio.Semaphore(aMaxConn)
        Tasks = [asyncio.create_task(self._GetWithSem(Url, Sem)) for Url in aUrls]
        return await asyncio.gather(*Tasks)
