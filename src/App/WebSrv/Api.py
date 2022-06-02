'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
'''

import asyncio
import json
#
from Inc.DB.DbList import TDbList
from IncP.ApiWeb import TApiBase, TWebClient
from IncP.Download import TDownload, TDHeaders, GetSoup, GetUrlSoup
from IncP.Scheme import TScheme
from IncP.Utils import GetNestedKey, FilterKey, FilterKeyErr


class TApiPlugin():
    def __init__(self, aArgs: dict = {}):
        self.Args = aArgs
        self.WebSock = None

    async def WebSockSend(self, aData):
        if (self.WebSock):
            Dbl, Id = self.WebSock
            RecNo = Dbl.FindField('Id', Id)
            if (RecNo is not None):
                Dbl.RecNo = RecNo
                WS = Dbl.Rec.GetField('WS')
                await WS.send_json(aData)

    async def WebSockInit(self, aPath, aData):
        self.WebSock = aData['ws']
        await asyncio.sleep(0.1)
        await self.WebSockSend({'Data': 'Ask server ' + aPath})
        aData.pop('ws')

    async def WebSockDbl(self, aPath, aData) -> dict:
        Url = 'web/get_hand_shake'
        await self.WebSockSend({'Data': Url})
        DataApi = await Api.WebClient.Send(Url)
        Err = FilterKeyErr(DataApi, True)
        if (Err):
            await self.WebSockSend({'Data': Err})
            return DataApi

        await self.WebSockSend({'Data': aPath})
        DataApi = await self.Args['WebClient'].Send(aPath, aData)
        Err = FilterKeyErr(DataApi, True)
        if (Err):
            await self.WebSockSend({'Data': Err})
            return DataApi

        DblJ = GetNestedKey(DataApi, 'Data.Data')
        if (DblJ):
            Res = {'Data': TDbList().Import(DblJ)}
        else:
            Res = {'Type': 'Err', 'Data': 'Err ' + aPath}
            await self.WebSockSend(Res)
        return Res

    async def Exec(self, aPath: str, aData: dict) -> dict:
        raise NotImplementedError()


class get_scheme_test_all(TApiPlugin):
    Param = {'param': ['cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: str):
        await self.WebSockSend({'Data': aUrl})
        Err = FilterKeyErr(aData)
        if (Err):
            self.Res.append([aUrl, str(aData['Data'])])
        else:
            Soup = GetSoup(aData['Data'])
            Scheme = self.Hash[aUrl]
            Scheme.Parse(Soup)
            if (Scheme.Err):
                self.Res.append([aUrl, Scheme.Err])

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_scheme_not_empty', aData)
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('Data')

        self.Hash = {}
        self.Res = []

        await self.WebSockSend({'Data': 'Check items %s' % len(Dbl)})
        for Rec in Dbl:
            SchemeStr = Rec.GetField('scheme')
            Scheme = TScheme(SchemeStr)
            Urls = Scheme.GetUrl()
            for Url in Urls:
                self.Hash[Url] = Scheme
            #break

        Download = TDownload()
        Download.Opt.update({'Headers': TDHeaders(), 'OnGet': self.cbOnGet, 'Decode': True})
        await Download.Gets(self.Hash.keys())

        await self.WebSockSend({'Data': 'Done'})
        return {'Data': self.Res}


class get_sites_check_file(TApiPlugin):
    Param = {'param': ['file', 'cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: str):
        Ok = aData.get('Status') == 200
        await self.WebSockSend({'Data': '%s %s' % (aUrl, Ok)})
        if (Ok):
            self.Res.append([aUrl])

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_sites', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('Data')

        File = aData.get('file')
        Urls = ['%s%s' % (x, File) for x in Dbl.ExportList('url')]

        await self.WebSockSend({'Data': 'Check items %s' % len(Dbl)})
        self.Res = []
        Download = TDownload()
        Download.Opt.update({'Headers': TDHeaders(), 'FakeRead': True, 'OnGet': self.cbOnGet})
        await Download.Gets(Urls)

        await self.WebSockSend({'Data': 'Done'})
        return {'Data': self.Res}


class get_scheme_find(TApiPlugin):
    Param = {'param': ['url', 'cnt', 'ws']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_scheme_not_empty', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('Data')

        Url = aData.get('url')
        await self.WebSockSend({'Data': 'Load ' + Url})
        Soup = await GetUrlSoup(Url)
        if (not Soup):
            return {'Type': 'Err', 'Data': 'Error loading %s' % (Url)}

        await self.WebSockSend({'Data': 'Check items %s' % len(Dbl)})
        Arr = []
        for Rec in Dbl:
            Url = Rec.GetField('url')
            await self.WebSockSend({'Data': Url})

            Scheme = TScheme(Rec.GetField('scheme'))
            Scheme.Parse(Soup)
            if (Scheme.Pipe):
                Arr.append([Url, Scheme.Pipe])

        await self.WebSockSend({'Data': 'Done'})
        Res = {'Data': Arr}
        return Res

class get_sites_grep(TApiPlugin):
    Param = {'param': ['file', 'filter', 'cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: dict):
        if (aData.get('Type') == 'Err'):
            await self.WebSockSend({'Data': '%s, Err: %s' % (aUrl, aData.get('Data'))})
        else:
            if (self.Filter in aData.get('Data')):
                await self.WebSockSend({'Data': '%s %s' % (aUrl, self.Filter)})
                self.Res.append([aUrl])
            else:
                await self.WebSockSend({'Data': aUrl})

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_sites', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('Data')

        self.Size = len(Dbl)
        await self.WebSockSend({'Data': 'Check items %s' % self.Size})

        File = aData.get('file')
        Urls = ['%s%s' % (x, File) for x in Dbl.ExportList('url')]

        self.Res = []
        self.Filter = aData.get('filter')
        Download = TDownload()
        Download.Opt.update({'Headers': TDHeaders(), 'OnGet': self.cbOnGet, 'Decode': True})
        await Download.Gets(Urls)

        await self.WebSockSend({'Data': 'Done'})
        return {'Data': self.Res}


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
        DataApi = await Api.WebClient.Send('web/get_hand_shake')
        if (GetNestedKey(DataApi, 'Type') == 'Err'):
            return DataApi.get('Data')

        DataApi = await self.Args['WebClient'].Send('web/get_scheme', aData)
        DblJ = GetNestedKey(DataApi, 'Data.Data')
        if (DblJ):
            Dbl = TDbList().Import(DblJ)
            Scheme = TScheme(Dbl.Rec.GetField('scheme'))
            DataApi['IsJson'] = Scheme.IsJson()
            DataApi['Url'] = Scheme.GetUrl()[0]
        return DataApi


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
        self.PluginAdd(get_sites_check_file, {'WebClient': self.WebClient})
        self.PluginAdd(get_sites_grep, {'WebClient': self.WebClient})
        self.PluginAdd(set_scheme, {'WebClient': self.WebClient})

    async def DoAuthRequest(self, aUser: str, aPassw: str):
        return True

    async def DefHandler(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)


Api = TApi()
