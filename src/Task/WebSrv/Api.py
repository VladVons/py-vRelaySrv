# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import asyncio
import json
#
from Inc.DbList import TDbListSafe
from Inc.Util.Obj import DeepGet
from Inc.Misc.Misc import FilterKey, FilterKeyErr
from Inc.WebSrv.WebApi import TApiBase, TWebClient
from IncP.Download import TDownload, TDHeaders, GetSoup, GetSoupUrl
from IncP.Scheme.Scheme import TScheme
from IncP.Scheme.SchemeApi import TSchemeApi


class TApiPlugin():
    def __init__(self, aArgs: dict = None):
        if (aArgs is None):
            aArgs = {}

        self.Args = aArgs
        self.WebSock = None
        self.Res = []
        self.Hash = {}

    async def WebSockSend(self, aData):
        if (self.WebSock):
            Dbl, Id = self.WebSock
            RecNo = Dbl.FindField('id', Id)
            if (RecNo >= 0):
                Dbl.RecNo = RecNo
                WS = Dbl.Rec.GetField('WS')
                await WS.send_json(aData)

    async def WebSockInit(self, aPath, aData):
        self.Res = []
        self.WebSock = aData['ws']
        await asyncio.sleep(0.1)
        await self.WebSockSend({'data': 'Ask server ' + aPath})
        aData.pop('ws')

    async def WebSockDbl(self, aPath, aData) -> dict:
        Url = 'web/get_hand_shake'
        await self.WebSockSend({'data': Url})
        DataApi = await Api.WebClient.Send(Url)
        Err = FilterKeyErr(DataApi, True)
        if (Err):
            await self.WebSockSend({'data': Err})
            return DataApi

        await self.WebSockSend({'data': aPath})
        DataApi = await self.Args['web_client'].Send(aPath, aData)
        Err = FilterKeyErr(DataApi, True)
        if (Err):
            await self.WebSockSend({'data': Err})
            return DataApi

        DblJ = DeepGet(DataApi, 'data.data')
        if (DblJ):
            Res = {'data': TDbListSafe().Import(DblJ)}
        else:
            Res = {'type': 'err', 'data': 'err ' + aPath}
            await self.WebSockSend(Res)
        return Res

    async def Exec(self, aPath: str, aData: dict) -> dict:
        raise NotImplementedError()


class get_scheme_test_all(TApiPlugin):
    Param = {'param': ['cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: str):
        await self.WebSockSend({'data': aUrl})
        Err = FilterKeyErr(aData)
        if (Err):
            self.Res.append([aUrl, str(aData['data'])])
        else:
            Soup = GetSoup(aData['data'])
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
        Dbl = Data.get('data')

        self.Hash = {}

        await self.WebSockSend({'data': 'Check items %s' % len(Dbl)})
        for Rec in Dbl:
            SchemeStr = Rec.GetField('scheme')
            Scheme = TScheme(SchemeStr)
            Urls = Scheme.GetUrl()
            for Url in Urls:
                self.Hash[Url] = Scheme
            #break

        Download = TDownload()
        Download.Opt.update({'headers': TDHeaders(), 'on_get': self.cbOnGet, 'decode': True})
        await Download.Gets(self.Hash.keys())

        await self.WebSockSend({'data': 'done'})
        return {'data': self.Res}


class get_sites_check_file(TApiPlugin):
    Param = {'param': ['file', 'cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: str):
        Ok = aData.get('status') == 200
        await self.WebSockSend({'data': '%s %s' % (aUrl, Ok)})
        if (Ok):
            self.Res.append([aUrl])

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_sites', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('data')

        File = aData.get('file')
        Urls = ['%s%s' % (x, File) for x in Dbl.ExportList('url')]

        await self.WebSockSend({'data': 'Check items %s' % len(Dbl)})
        Download = TDownload()
        Download.Opt.update({'headers': TDHeaders(), 'fake_read': True, 'on_get': self.cbOnGet})
        await Download.Gets(Urls)

        await self.WebSockSend({'data': 'done'})
        return {'data': self.Res}


class get_scheme_find(TApiPlugin):
    Param = {'param': ['url', 'cnt', 'ws']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_scheme_not_empty', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('data')

        Url = aData.get('url')
        await self.WebSockSend({'data': 'Load ' + Url})

        Data = await GetSoupUrl(Url)
        Err = FilterKeyErr(Data)
        if (Err):
            return {'type': 'err', 'data': 'Error loading %s, %s' % (Url, Err)}

        await self.WebSockSend({'data': 'Check items %s' % len(Dbl)})
        Arr = []
        for Rec in Dbl:
            Url = Rec.GetField('url')
            await self.WebSockSend({'data': Url})

            Scheme = TScheme(Rec.GetField('scheme'))
            Scheme.Parse(Data.get('soup'))
            if (Scheme.Pipe):
                Arr.append([Url, Scheme.Pipe])

        await self.WebSockSend({'data': 'done'})
        Res = {'data': Arr}
        return Res


class get_sites_grep(TApiPlugin):
    Param = {'param': ['file', 'filter', 'cnt', 'ws']}

    def __init__(self, aArgs: dict):
        super().__init__(aArgs)
        self.Filter = None

    async def cbOnGet(self, aUrl: str, aData: dict):
        Err = FilterKeyErr(aData)
        if (Err):
            await self.WebSockSend({'data': '%s, err: %s' % (aUrl, Err)})
        else:
            if (self.Filter in aData.get('data')):
                await self.WebSockSend({'data': '%s %s' % (aUrl, self.Filter)})
                self.Res.append([aUrl])
            else:
                await self.WebSockSend({'data': aUrl})

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_sites', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data
        Dbl = Data.get('data')

        await self.WebSockSend({'data': 'Check items %s' % len(Dbl)})

        File = aData.get('file')
        Urls = ['%s%s' % (x, File) for x in Dbl.ExportList('url')]

        self.Filter = aData.get('filter')
        Download = TDownload()
        Download.Opt.update({'headers': TDHeaders(), 'on_get': self.cbOnGet, 'decode': True})
        await Download.Gets(Urls)

        await self.WebSockSend({'data': 'done'})
        return {'data': self.Res}


class get_sites_app_json(TApiPlugin):
    Param = {'param': ['cnt', 'ws']}

    async def cbOnGet(self, aUrl: str, aData: dict):
        Err = FilterKeyErr(aData)
        if (Err):
            await self.WebSockSend({'data': '%s, err: %s' % (aUrl, Err)})
        else:
            Soup = GetSoup(aData.get('data'))
            if (Soup):
                AppData = TSchemeApi.app_json(Soup)
                if (AppData):
                    self.Res.append([aUrl])
                    await self.WebSockSend({'data': '%s, %s' % (aUrl, bool(AppData))})

    async def Exec(self, aPath: str, aData: dict) -> dict:
        await self.WebSockInit(aPath, aData)
        Data = await self.WebSockDbl('web/get_scheme_not_empty', FilterKey(aData, ['cnt'], dict))
        Err = FilterKeyErr(Data)
        if (Err):
            return Data

        Urls = []
        Dbl = Data.get('data')
        for Rec in Dbl:
            if (not Rec.GetField('protected')):
                Scheme = TScheme(Rec.GetField('scheme'))
                Url = Scheme.GetUrl()[0]
                Urls.append(Url)
        await self.WebSockSend({'data': 'Check items %s' % len(Urls)})

        self.Res = []
        Download = TDownload()
        Download.Opt.update({'headers': TDHeaders(), 'on_get': self.cbOnGet, 'decode': True})
        await Download.Gets(Urls)

        await self.WebSockSend({'data': 'done'})
        return {'data': self.Res}



class get_scheme_test(TApiPlugin):
    Param = {'param': ['scheme']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        if (not aData['scheme']):
            return {'type': 'err', 'data': 'No scheme'}

        try:
            Scheme = TScheme(aData['scheme'])
        except ValueError as E:
            return {'type': 'err', 'data': str(E)}

        Urls = Scheme.GetUrl()
        if (not Urls):
            return {'type': 'err', 'data': 'No product url'}

        Url = Urls[0]
        Data = await GetSoupUrl(Url)
        Err = FilterKeyErr(Data)
        if (Err):
            return {'type': 'err', 'data': 'Error loading %s, %s' % (Url, Err)}

        try:
            Res = Scheme.Parse(Data.get('soup')).GetData(['err', 'pipe', 'warn'])
            json.dumps(Res)
        except Exception as E:
            Res = {'type': 'err', 'data': str(E)}
        return Res


class set_scheme(TApiPlugin):
    Param = {'param': ['scheme', 'trust']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        Scheme = TScheme(aData.get('scheme'))
        Url = Scheme.GetUrl()[0]
        Data = await GetSoupUrl(Url)
        Err = FilterKeyErr(Data)
        if (Err):
            return {'type': 'err', 'data': 'Error loading %s, %s' % (Url, Err)}

        Scheme.Parse(Data.get('soup'))
        if (Scheme.Err):
            Res = {'type': 'err', 'data': Scheme.Err}
        else:
            Res = await self.Args['web_client'].Send('web/set_scheme', aData)
        return Res


class get_scheme_by_id(TApiPlugin):
    Param = {'param': ['id']}

    async def Exec(self, aPath: str, aData: dict) -> dict:
        DataApi = await Api.DefHandler('get_hand_shake')
        Err = FilterKeyErr(DataApi)
        if (Err):
            return Err

        DataApi = await self.Args['web_client'].Send('web/get_scheme_by_id', aData)
        Err = FilterKeyErr(DataApi)
        if (not Err):
            DblJ = DeepGet(DataApi, 'data.data')
            Dbl = TDbListSafe().Import(DblJ)
            Scheme = TScheme(Dbl.Rec.GetField('scheme'))
            DataApi['is_json'] = Scheme.IsJson()
            DataApi['url'] = Scheme.GetUrl()[0]
        return DataApi


class TApi(TApiBase):
    def __init__(self):
        super().__init__()

        self.Url = {
            'get_scheme_empty':         {'param': ['cnt']},
            'get_scheme_not_empty':     {'param': ['cnt']},
            'get_scheme_mederate':      {'param': []},
        }

        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

        self.PluginAdd(get_scheme_find, {'web_client': self.WebClient})
        self.PluginAdd(get_scheme_test_all, {'web_client': self.WebClient})
        self.PluginAdd(get_scheme_test)
        self.PluginAdd(get_scheme_by_id, {'web_client': self.WebClient})
        self.PluginAdd(get_sites_check_file, {'web_client': self.WebClient})
        self.PluginAdd(get_sites_grep, {'web_client': self.WebClient})
        self.PluginAdd(get_sites_app_json, {'web_client': self.WebClient})
        self.PluginAdd(set_scheme, {'web_client': self.WebClient})

    async def _DoAuthRequest(self, aUser: str, aPassw: str):
        return True

    async def DefHandler(self, aPath: str, aData: dict = None) -> dict: #//
        if (aData is None):
            aData = {}
        return await self.WebClient.Send(f'web/{aPath}', aData)


Api = TApi()
