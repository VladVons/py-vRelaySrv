'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
'''


import base64
import json
import time
import aiohttp
from aiohttp import web
#
from Inc.DB.DbList import TDbList
from IncP.Log import Log
from IncP.Utils import GetNestedKey


class TApiBase():
    def __init__(self):
        self.Url = {}
        self.DefMethod = None
        self.Plugin = {}

    @staticmethod
    def GetMethodName(aPath: str) -> str:
        return 'path_' + aPath.replace('/', '_')

    @staticmethod
    def CheckParam(aParam: dict, aPattern: list):
        Diff = set(aPattern) - set(aParam)
        if (Diff):
            return 'param not set. %s' % Diff

        Diff = set(aParam) - set(aPattern)
        if (Diff):
            return 'param unknown. %s' % Diff

    def PluginAdd(self, aCls: object, aArgs: dict = {}) -> object:
        Name = aCls.__name__
        if (not self.Url.get(Name)):
            Res = aCls(aArgs)
            self.Url[Name] = aCls.Param
            self.Url[Name]['Class'] = Res
            return Res

    async def Call(self, aPath: str, aParam: dict) -> dict:
        UrlInf = self.Url.get(aPath)
        if (not UrlInf):
            return {'Type': 'Err', 'Data': 'unknown url %s' % (aPath)}

        MethodName = self.GetMethodName(aPath)
        Method = getattr(self, MethodName, None)
        if (not Method):
            Class = UrlInf.get('Class')
            if (Class):
                Method = getattr(Class, 'Exec', self.DefMethod)
            else:
                Method = self.DefMethod

            if (not Method):
               return {'Type': 'Err', 'Data': 'unknown method %s' % (aPath)}

        ParamInf = UrlInf.get('param')
        if (ParamInf) and (ParamInf[0] == '*'):
            ParamInf = aParam.keys()

        ErrMsg = self.CheckParam(aParam, ParamInf)
        if (ErrMsg):
            Log.Print(1, 'e', ErrMsg)
            Res = {'Type': 'Err', 'Data': ErrMsg}
        else:
            try:
                Data = await Method(aPath, aParam)
            except Exception as E:
                Data = None
                Log.Print(1, 'x', 'Call()', aE = E)
            Res = {'Data': Data}
        return Res

    async def AuthRequest(self, aRequest: web.Request, aAuth: bool = True) -> bool:
        if (aAuth):
            Auth = aRequest.headers.get('Authorization')
            if (Auth):
                User, Passw = base64.b64decode(Auth.split()[1]).decode().split(':')
                return await self.DoAuthRequest(User, Passw)
        else:
            return True

    async def DoAuthRequest(self, aUser: str, aPassw: str) -> bool:
        raise NotImplementedError()


class TWebClient():
    def __init__(self, aAuth: dict = None):
        if (aAuth is None):
            aAuth = {}
        self.Auth = aAuth

    async def Send(self, aPath: str, aPost: dict = {}):
        Auth = aiohttp.BasicAuth(self.Auth.get('User'), self.Auth.get('Password'))
        Url = 'http://%s:%s/%s' % (self.Auth.get('Server'), self.Auth.get('Port'), aPath)
        TimeAt = time.time()
        try:
            async with aiohttp.ClientSession(auth=Auth) as Session:
                async with Session.post(Url, json=aPost) as Response:
                    Data = await Response.json()
                    Res = {'Data': Data, 'Status': Response.status, 'Time': round(time.time() - TimeAt, 2)}
        except (aiohttp.ContentTypeError, aiohttp.ClientConnectorError, aiohttp.InvalidURL) as E:
            Log.Print(1, 'x', 'Send(). %s' % (Url), aE = E)
            Res = {'Type': 'Err', 'Data': E, 'Msg': Url, 'Time': round(time.time() - TimeAt, 2)}
        return Res


class TWebSockClient():
    def __init__(self, aAuth: dict = None):
        if (aAuth is None):
            aAuth = {}
        self.Auth = aAuth
        self.OnMessage = None

    async def Connect(self, aPath: str, aParam: dict = {}):
        Auth = aiohttp.BasicAuth(self.Auth.get('User'), self.Auth.get('Password'))
        Url = 'http://%s:%s/%s' % (self.Auth.get('Server'), self.Auth.get('Port'), aPath)
        async with aiohttp.ClientSession(auth=Auth) as Session:
            async with Session.ws_connect(Url, params=aParam) as self.WS:
                async for Msg in self.WS:
                    if (Msg.type == aiohttp.WSMsgType.TEXT):
                        Data = json.loads(Msg.data)
                        await self.DoMessage(Data)
                    elif (Msg.type == aiohttp.WSMsgType.CLOSED) or (Msg.type == aiohttp.WSMsgType.ERROR):
                        break

    async def Close(self):
        if (self.WS):
            await self.WS.close()

    async def Send(self, aData: dict):
        await self.WS.send_json(aData)

    async def DoMessage(self, aData):
        if (self.OnMessage):
            await self.OnMessage(aData)


class TWebSockSrv():
    def __init__(self):
        self.DblWS = TDbList([('WS', web.WebSocketResponse), ('Id', str)])
        self.Api = None

    async def Handle(self, aRequest: web.Request) -> web.WebSocketResponse:
        WS = web.WebSocketResponse()
        await WS.prepare(aRequest)
        try:
            #Id = aRequest.headers.get('Sec-WebSocket-Key')
            Id = aRequest.query.get('id')
            self.DblWS.RecAdd([WS, Id])
            async for Msg in WS:
                if (Msg.type == web.WSMsgType.text):
                    Plugin = aRequest.query.get('plugin')
                    if (Plugin):
                        Class = GetNestedKey(self.Api.Url, Plugin + '.Class')
                        if (Class is None):
                            await WS.send_json({'Type': 'Err', 'Data': 'Unknown plugin %s' % (Plugin)})
                        else:
                            Data = Msg.json()
                            Param = Data.get('Param', {})
                            Param['ws'] = (self.DblWS, Param.get('ws'))
                            await Class.Exec(Plugin, Param)
        except Exception as E:
            Log.Print(1, 'x', 'AddHandler()', aE=E)
        finally:
            self.DblWS.RecNo = 0
            RecNo = self.DblWS.FindField('WS', WS)
            self.DblWS.RecPop(RecNo)
        return WS
