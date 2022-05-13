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
from IncP.Scheme import TScheme
from IncP.Download import TDownload, THeaders
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
            'set_scheme':               {'param': ['id', 'scheme', 'url']}
        }

        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

    @staticmethod
    async def GetSoup(aUrl: str) -> BeautifulSoup:
        Download = TDownload(aHeaders = THeaders())
        UrlDown = await Download.Get(aUrl, True)
        if (not UrlDown.get('Err')):
            Data = UrlDown['Data']
            return BeautifulSoup(Data, 'lxml')

    async def DefHandler(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

    async def path_get_scheme(self, aPath: str, aData: dict) -> dict:
        Data = await self.DefHandler(aPath, aData)
        DataDbL = GetNestedKey(Data, 'Data.Data')
        if (DataDbL):
            Dbl = TDbList().Import(DataDbL)
            Scheme = TScheme(Dbl.Rec.GetField('scheme'))
            Data['IsJson'] = Scheme.IsJson()
            Data['Url'] = Scheme.GetUrl()
        return Data

    async def path_set_scheme(self, aPath: str, aData: dict) -> dict:
        Scheme = TScheme(aData.get('scheme'))
        Url = Scheme.GetUrl()
        if (not Url.startswith(aData.get('url'))):
            return {'Err': 'Url mismatch'}

        Soup = await self.GetSoup(Url)
        if (not Soup):
            return {'Err': 'Error loading %s' % (Url)}

        Parsed = Scheme.Parse(Soup)
        if (Parsed['Err']):
            Res = {'Err': Parsed['Err']}
        else:
            aData.pop('url', None)
            Res = await self.DefHandler(aPath, aData)
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
            Scheme = TScheme(Rec.GetField('scheme'))
            Parsed = Scheme.Parse(Soup)
            Pipe = GetNestedKey(Parsed, 'Data.Product.Pipe')
            if (Pipe):
                Arr.append([Rec.GetField('url'), Pipe])
        Res = {'Data': Arr}
        return Res

    async def path_get_scheme_test(self, aPath: str, aData: dict) -> dict:
        if (not aData['scheme']):
            return {'Err': 'No scheme'}

        try:
            Scheme = TScheme(aData['scheme'])
        except ValueError as E:
            return {'Err': str(E)}

        Url = Scheme.GetUrl()
        if (not Url):
            return {'Err': 'No Product.Info.Url %s' % (Url)}

        Soup = await self.GetSoup(Url)
        if (Soup):
            Res = Scheme.Parse(Soup)
        else:
            Res = {'Err': 'Error loading %s' % (Url)}
        return Res


Api = TApi()
