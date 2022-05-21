'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
'''

import asyncio
import json
from bs4 import BeautifulSoup
#
from IncP.ApiWeb import TApiBase, TWebClient
from IncP.Scheme import TScheme
from IncP.Download import TDownload, THeaders, GetUrlSoup
from IncP.Utils import GetNestedKey
from Inc.DB.DbList import TDbList


class TApiPlugin():
    def __init__(self, aArgs: dict = {}):
        self.Args = aArgs
        self.WebSock = None

    async def WebSocketSend(self, aData):
        #WS = self.Args.get('WebSocket')
        if (self.WebSock):
            Dbl, Id = self.WebSock
            RecNo = Dbl.FindField('Id', Id)
            if (RecNo is not None):
                Dbl.RecNo = RecNo
                WS = Dbl.Rec.GetField('WS')
                await WS.send_json(aData)

    async def Exec(self, aPath: str, aData: dict) -> dict:
        raise NotImplementedError()


class get_scheme_test_all(TApiPlugin):
    Param = {'param': ['cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: str):
        await self.WebSocketSend({'Data': aUrl})
        if (aData.get('Type') == 'Err'):
            self.Res.append([aUrl, str(aData['Data'])])
        else:
            Soup = BeautifulSoup(aData['Data'], 'lxml')
            Scheme = self.Hash[aUrl]
            Scheme.Parse(Soup)
            if (Scheme.Err):
                self.Res.append([aUrl, Scheme.Err])

    async def Exec(self, aPath: str, aData: dict) -> dict:
        self.WebSock = aData['ws']
        await asyncio.sleep(0.1)
        await self.WebSocketSend({'Data': 'Ask server'})

        aData.pop('ws')
        Data = await self.Args['WebClient'].Send('web/get_scheme_not_empty', aData)
        DblJ = GetNestedKey(Data, 'Data.Data')
        if (not DblJ):
            Res = {'Type': 'Err', 'Data': 'Error getting scheme'}
            await self.WebSocketSend(Res)
            return Res

        await self.WebSocketSend({'Data': 'Check'})
        self.Hash = {}
        self.Res = []
        Dbl = TDbList().Import(DblJ)
        for Rec in Dbl:
            SchemeStr = Rec.GetField('scheme')
            Scheme = TScheme(SchemeStr)
            Urls = Scheme.GetUrl()
            for Url in Urls:
                self.Hash[Url] = Scheme
            #break

        Download = TDownload(aHeaders = THeaders())
        Download.OnGet = self.cbOnGet
        await Download.Gets(self.Hash.keys())

        await self.WebSocketSend({'Data': 'Done'})
        return {'Data': self.Res}


class get_scheme_find(TApiPlugin):
    Param = {'param': ['url', 'ws']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        self.WebSock = aData['ws']
        await asyncio.sleep(0.1)
        await self.WebSocketSend({'Data': 'Ask server'})

        Data = await self.Args['WebClient'].Send('web/get_scheme_not_empty', {'cnt': 100})

        DblJ = GetNestedKey(Data, 'Data.Data')
        if (not DblJ):
            return {'Type': 'Err', 'Data': 'Error getting scheme'}
        Dbl = TDbList().Import(DblJ)

        Url = aData.get('url')
        await self.WebSocketSend({'Data': 'Load ' + Url})
        Soup = await GetUrlSoup(Url)
        if (not Soup):
            return {'Type': 'Err', 'Data': 'Error loading %s' % (Url)}

        await self.WebSocketSend({'Data': 'Check'})
        Arr = []
        for Rec in Dbl:
            Url = Rec.GetField('url')
            await self.WebSocketSend({'Data': Url})

            Scheme = TScheme(Rec.GetField('scheme'))
            Scheme.Parse(Soup)
            if (Scheme.Pipe):
                Arr.append([Url, Scheme.Pipe])

        await self.WebSocketSend({'Data': 'Done'})
        Res = {'Data': Arr}
        return Res


class get_scheme_test(TApiPlugin):
    Param = {'param': ['scheme']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        if (not aData['scheme']):
            return {'Type': 'Err', 'Data': 'No scheme'}

        try:
            Scheme = TScheme(aData['scheme'])
        except ValueError as E:
            return {'Type': 'Err', 'Data': str(E)}

        Urls = Scheme.GetUrl()
        if (not Urls):
            return {'Type': 'Err', 'Data': 'No product url'}

        Url = Urls[0]
        Soup = await GetUrlSoup(Url)
        if (Soup):
            Res = Scheme.Parse(Soup).GetData(['Err', 'Pipe'])
            try:
                json.dumps(Res)
            except Exception as E:
                Res = {'Type': 'Err', 'Data': str(E)}
        else:
            Res = {'Type': 'Err', 'Data': 'Error loading %s' % (Url)}
        return Res


class set_scheme(TApiPlugin):
    Param = {'param': ['id', 'scheme', 'url']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        Scheme = TScheme(aData.get('scheme'))
        Url = Scheme.GetUrl()[0]
        if (not Url.startswith(aData.get('url'))):
            return {'Err': 'Url mismatch'}

        Soup = await GetUrlSoup(Url)
        if (not Soup):
            return {'Type': 'Err', 'Data': 'Error loading %s' % (Url)}

        Scheme.Parse(Soup)
        if (Scheme.Err):
            Res = {'Type': 'Err', 'Data': Scheme.Err}
        else:
            aData.pop('url', None)
            Res = await self.Args['WebClient'].Send('web/set_scheme', aData)
        return Res


class get_scheme(TApiPlugin):
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

        self.PluginAdd(get_scheme_find, {'WebClient': self.WebClient})
        self.PluginAdd(get_scheme_test_all, {'WebClient': self.WebClient})
        self.PluginAdd(get_scheme_test)
        self.PluginAdd(get_scheme, {'WebClient': self.WebClient})
        self.PluginAdd(set_scheme, {'WebClient': self.WebClient})

    async def DefHandler(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)


Api = TApi()
