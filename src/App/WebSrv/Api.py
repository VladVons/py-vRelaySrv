'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
'''

import json
from bs4 import BeautifulSoup
#
from IncP.ApiWeb import TApiBase, TWebClient
from IncP.Scheme import TScheme
from IncP.Download import TDownload, THeaders, GetUrlSoup
from IncP.Utils import GetNestedKey
from Inc.DB.DbList import TDbList


class get_scheme_test_all():
    Param = {'param': ['cnt']}

    def __init__(self):
        self.Hash = {}
        self.Res = []

    async def cbOnGet(self, aUrl: str, aData: str):
        if (aData.get('Err')):
            self.Res.append([aUrl, aData['Err']])
        else:
            print(aUrl)
            Soup = BeautifulSoup(aData['Data'], 'lxml')
            Scheme = self.Hash[aUrl]
            Scheme.Parse(Soup)
            if (Scheme.Err):
                self.Res.append([aUrl, Scheme.Err])

    async def Exec(self, aPath: str, aData: dict) -> dict:
        Data = await self.Args['WebClient'].Send('web/get_scheme_not_empty', aData)
        DblJ = GetNestedKey(Data, 'Data.Data')
        if (not DblJ):
            return {'Err': 'Error getting scheme'}

        Dbl = TDbList().Import(DblJ)
        for Rec in Dbl:
            SchemeStr = Rec.GetField('scheme')
            Scheme = TScheme(SchemeStr)
            Urls = Scheme.GetUrl()
            for Url in Urls:
                self.Hash[Url] = Scheme

        Download = TDownload(aHeaders = THeaders())
        Download.OnGet = self.cbOnGet
        await Download.Gets(self.Hash.keys())
        print('Done')
        return {'Data': self.Res}


class get_scheme_find():
    Param = {'param': ['url']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        Data = await self.Args['WebClient'].Send('web/get_scheme_not_empty', {'cnt': 100})

        DblJ = GetNestedKey(Data, 'Data.Data')
        if (not DblJ):
            return {'Err': 'Error getting scheme'}
        Dbl = TDbList().Import(DblJ)

        Url = aData.get('url')
        Soup = await GetUrlSoup(Url)
        if (not Soup):
            return {'Err': 'Error loading %s' % (Url)}

        Arr = []
        for Rec in Dbl:
            Scheme = TScheme(Rec.GetField('scheme'))
            Scheme.Parse(Soup)
            if (Scheme.Pipe):
                Arr.append([Rec.GetField('url'), Scheme.Pipe])
        Res = {'Data': Arr}
        return Res


class get_scheme_test():
    Param = {'param': ['scheme']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        if (not aData['scheme']):
            return {'Err': 'No scheme'}

        try:
            Scheme = TScheme(aData['scheme'])
        except ValueError as E:
            return {'Err': str(E)}

        Urls = Scheme.GetUrl()
        if (not Urls):
            return {'Err': 'No product url'}

        Url = Urls[0]
        Soup = await GetUrlSoup(Url)
        if (Soup):
            Res = Scheme.Parse(Soup).GetData(['Err', 'Pipe'])
            try:
                json.dumps(Res)
            except Exception as E:
                Res = {'Err': str(E)}
        else:
            Res = {'Err': 'Error loading %s' % (Url)}
        return Res


class set_scheme():
    Param = {'param': ['id', 'scheme', 'url']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        Scheme = TScheme(aData.get('scheme'))
        Url = Scheme.GetUrl()[0]
        if (not Url.startswith(aData.get('url'))):
            return {'Err': 'Url mismatch'}

        Soup = await GetUrlSoup(Url)
        if (not Soup):
            return {'Err': 'Error loading %s' % (Url)}

        Scheme.Parse(Soup)
        if (Scheme.Err):
            Res = {'Err': Scheme.Err}
        else:
            aData.pop('url', None)
            Res = await self.DefHandler(aPath, aData)
        return Res


class get_scheme():
    Param = {'param': ['id']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        Data = await self.Args['WebClient'].Send('web/get_scheme', aData)
        DataDbl = GetNestedKey(Data, 'Data.Data')
        if (DataDbl):
            Dbl = TDbList().Import(DataDbl)
            Scheme = TScheme(Dbl.Rec.GetField('scheme'))
            Data['IsJson'] = Scheme.IsJson()
            Data['Url'] = Scheme.GetUrl()[0]
        return Data


class TApi(TApiBase):
    def __init__(self):
        super().__init__()

        self.Url = {
            'get_scheme_empty':         {'param': ['cnt']},
            'get_scheme_not_empty':     {'param': ['cnt']}
        }

        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

        self.AddPlugin(get_scheme_find, {'WebClient': self.WebClient})
        self.AddPlugin(get_scheme_test_all, {'WebClient': self.WebClient})
        self.AddPlugin(get_scheme_test)
        self.AddPlugin(get_scheme, {'WebClient': self.WebClient})
        self.AddPlugin(set_scheme)

    async def DefHandler(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

Api = TApi()
