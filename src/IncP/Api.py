"""
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
"""


import time
import aiohttp
#
from IncP.Log import Log


class TApiBase():
    def __init__(self, aAuth: dict = {}):
        self.Auth = aAuth

    async def _Send(self, aPath: str, aPost: dict = {}):
        Auth = aiohttp.BasicAuth(self.Auth.get('User'), self.Auth.get('Password'))
        Url = 'http://%s:%s/%s' % (self.Auth.get('Server'), self.Auth.get('Port'), aPath)
        TimeAt = time.time()
        try:
            async with aiohttp.ClientSession(auth=Auth) as Session:
                async with Session.post(Url, json=aPost) as Response:
                    Data = await Response.json()
                    Res = {'Data': Data, 'Status': Response.status, 'Time': time.time() - TimeAt}
        except (aiohttp.ContentTypeError, aiohttp.ClientConnectorError, aiohttp.InvalidURL) as E:
            ErrMsg = Log.Print(1, 'x', '_Send(). %s' % (Url), aE = E)
            Res = {'Err': E, 'Msg': ErrMsg}
        return Res