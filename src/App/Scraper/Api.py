"""
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
"""


import os
import asyncio
import aiohttp
#
from IncP.Log import Log


class TApi():
    def __init__(self, aAuth: dict = {}):
        self.Auth = aAuth

    async def _Send(self, aPath: str, aPost: dict = {}):
        Auth = aiohttp.BasicAuth(self.Auth.get('User'), self.Auth.get('Password'))
        Url = 'http://%s:%s/%s' % (self.Auth.get('Server'), self.Auth.get('Port'), aPath)
        try:
            async with aiohttp.ClientSession(auth=Auth) as Session:
                async with Session.post(Url, json=aPost) as Response:
                    Data = await Response.json()
                    return (Data, Response.status)
        except (aiohttp.client_exceptions.ContentTypeError, aiohttp.client_exceptions.ClientConnectorError) as E:
            Log.Print(1, 'x', '_Send()', aE = E)

    async def GetConfig(self):
        Data = {'user': self.Auth.get('User')}
        return await self._Send('get_config', Data)

    async def GetTask(self):
        return await self._Send('get_task')

    async def SendResult(self, aData: dict):
        return await self._Send('send_result', aData)

Api = TApi()
