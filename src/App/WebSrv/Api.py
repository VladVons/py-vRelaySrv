'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
'''

import json
from bs4 import BeautifulSoup
#
from IncP.ApiWeb import TApiBase, TWebClient
from IncP.Scheme import TSoupScheme
from IncP.Download import TDownload
from IncP.Utils import TJsonEncoder
from IncP.Utils import GetNestedKey
from Inc.DB.DbList import TDbList


class TApi(TApiBase):
    def __init__(self):
        super().__init__()

        self.Url = {
            'get_scheme_empty':         {'param': ['cnt']},
            'get_scheme_not_empty':     {'param': ['cnt']},
            'get_scheme':               {'param': ['id']},
            'get_scheme_find':          {'param': ['url']},
            'get_scheme_test':          {'param': ['scheme']},
            'set_scheme':               {'param': ['id', 'scheme']}
        }

        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

    @staticmethod
    async def GetSoup(aUrl: str) -> BeautifulSoup:
        Download = TDownload()
        UrlDown = await Download.Get(aUrl)
        if (not UrlDown.get('Err')):
            Data = UrlDown['Data']
            return BeautifulSoup(Data, 'lxml')

    async def DefHandler(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

    async def path_set_scheme(self, aPath: str, aData: dict) -> dict:
        Scheme = json.loads(aData.get('scheme'))
        Url = GetNestedKey(Scheme, 'Product.-Info.Url', '')
        Soup = await self.GetSoup(Url)
        if (Soup):
            Parsed = TSoupScheme.ParseKeys(Soup, Scheme)
            if (Parsed['Product'][2][0]):
                Res = {'Err': Parsed['Product'][2]}
            else:
                Res = await self.DefHandler(aPath, aData)
        else:
            Res = {'Err': 'Error loading %s' % (Url)}
        return Res

    async def path_get_scheme_find(self, aPath: str, aData: dict) -> dict:
        Data = await self.WebClient.Send('web/get_scheme_not_empty', {'cnt': 100})

        DataDbL = GetNestedKey(Data, 'Data.Data')
        if (not DataDbL):
            return {'Err': 'Error getting scheme'}
        DbL = TDbList().Import(DataDbL)

        Url = aData.get('url')
        Soup = await self.GetSoup(Url)
        if (not Soup):
            return {'Err': 'Error loading %s' % (Url)}

        Arr = []
        for Rec in DbL:
            Scheme = json.loads(Rec.GetField('scheme'))
            Parsed = TSoupScheme.ParseKeys(Soup, Scheme)
            if (Parsed['Product'][0]):
                Arr.append((Rec.GetField('url'), Parsed['Product'][0]))
        Res = {'Data': Arr}
        return Res

    async def path_get_scheme_test(self, aPath: str, aData: dict) -> dict:
        Scheme = aData['scheme']
        if (not Scheme):
            return {'Err': 'No scheme'}

        try:
            Scheme = json.loads(Scheme)
        except ValueError as E:
            return {'Err': str(E)}

        Url = GetNestedKey(Scheme, 'Product.-Info.Url')
        if (not Url):
            return {'Err': 'No Product.-Info.Url %s' % (Url)}

        Soup = await self.GetSoup(Url)
        if (Soup):
            Res = TSoupScheme.ParseKeys(Soup, Scheme)
        else:
            Res = {'Err': 'Error loading %s' % (Url)}
        return Res


Api = TApi()
