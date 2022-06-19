'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.17
License:     GNU, see LICENSE for more details
'''

from aiohttp import web
import aiohttp_session
import re
#
from .Api import Api
from IncP.Log import Log
from IncP.Utils import GetNestedKey
from Inc.DB.DbList import TDbList


class TSession():
    def __init__(self):
        self.Cnt = 0
        self.Data = {}

    async def Update(self, aRequest: web.Request):
        self.Data = await aiohttp_session.get_session(aRequest)
        if (self.Cnt % 5 == 0):
           await self.UpdateUserConfig()
        self.Cnt += 1

    @staticmethod
    def _CheckUserAccess(aUrl: str, aUrls: list):
        if (aUrls):
            for x in aUrls:
                try:
                    if (x.strip()) and (not x.startswith('-')) and (re.match(x, aUrl)):
                        return True
                except Exception as E:
                    Log.Print(1, 'e', 'CheckUserAccess()', aE = E)
                    return False
        return False

    def CheckUserAccess(self, aUrl: str):
        Grant = ['/$', '/form/login', '/form/about']
        Allow = self.Data.get('UserConf', {}).get('interface_allow', '').split() + Grant
        Deny = self.Data.get('UserConf', {}).get('interface_deny', '').split()
        return (self._CheckUserAccess(aUrl, Allow)) and (not self._CheckUserAccess(aUrl, Deny))

    async def UpdateUserConfig(self):
        UserId = self.Data['UserId']
        DataApi = await Api.DefHandler('get_user_config', {'id': UserId})
        DblJ = GetNestedKey(DataApi, 'Data.Data')
        if (DblJ):
            Conf = TDbList().Import(DblJ).ExportPair('name', 'data')
            self.Data['UserConf'] = Conf

Session = TSession()
