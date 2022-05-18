'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
'''


import time
import json
import aiohttp
from aiohttp import web
#
from Inc.DB.DbList import TDbList, TDbCond
from IncP.Log import Log


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

    def AddPlugin(self, aCls: object, aArgs: dict = {}):
        Name = aCls.__name__
        if (not self.Url.get('Name')):
            Class = aCls()
            Class.Args = aArgs
            self.Url[Name] = aCls.Param
            self.Url[Name]['Class'] = Class

    async def Call(self, aPath: str, aParam: str) -> dict:
        UrlInf = self.Url.get(aPath)
        if (not UrlInf):
            return {'Err': 'unknown url %s' % (aPath)}

        MethodName = self.GetMethodName(aPath)
        Method = getattr(self, MethodName, None)
        if (not Method):
            Class = UrlInf.get('Class')
            if (Class):
                Method = getattr(Class, 'Exec', self.DefMethod)
                if (not Method):
                    return {'Err': 'unknown method %s' % (MethodName)}

        ParamInf = UrlInf.get('param')
        if (ParamInf):
            Param = json.loads(aParam)
        else:
            Param = {}

        if (ParamInf) and (ParamInf[0] == '*'):
            ParamInf = Param.keys()

        ErrMsg = self.CheckParam(Param, ParamInf)
        if (ErrMsg):
            Log.Print(1, 'e', ErrMsg)
            Res = {'Err': ErrMsg}
        else:
            try:
                Data = await Method(aPath, Param)
            except Exception as E:
                Data = None
                Log.Print(1, 'x', 'Call()', aE = E)
            Res = {'Data': Data}
        return Res


class TWebClient():
    def __init__(self, aAuth: dict = {}):
        self.Auth = aAuth

    async def Send(self, aPath: str, aPost: dict = {}):
        Auth = aiohttp.BasicAuth(self.Auth.get('User'), self.Auth.get('Password'))
        Url = 'http://%s:%s/%s' % (self.Auth.get('Server'), self.Auth.get('Port'), aPath)
        TimeAt = time.time()
        try:
            async with aiohttp.ClientSession(auth=Auth) as Session:
                async with Session.post(Url, json=aPost) as Response:
                    Data = await Response.json()
                    Res = {'Data': Data, 'Status': Response.status, 'Time': time.time() - TimeAt}
        except (aiohttp.ContentTypeError, aiohttp.ClientConnectorError, aiohttp.InvalidURL) as E:
            ErrMsg = Log.Print(1, 'x', 'Send(). %s' % (Url), aE = E)
            Res = {'Err': E, 'Msg': ErrMsg, 'Time': time.time() - TimeAt}
        return Res


class TWebSockClient():
    def __init__(self, aAuth: dict = {}):
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


class TWebSockServer():
    def __init__(self):
        self.DblWS = TDbList([('WS', web.WebSocketResponse), ('Path', str), ('Query', dict)])
        self.OnReplay = None

    async def AddHandler(self, aRequest, aWS):
        await aWS.prepare(aRequest)
        try:
            self.DblWS.RecAdd([aWS, aRequest.path, dict(aRequest.query)])
            async for Msg in aWS:
                if (Msg.type == web.WSMsgType.text):
                    Data = {'Msg': Msg.json(), 'Path': aRequest.path, 'Query': dict(aRequest.query)}
                    await self.DoReplay(aWS, Data)
                #elif (Msg.type == web.MsgType.binary):
                #    await aWS.send_bytes(Msg.data)
                #elif (Msg.type == aiohttp.WSMsgType.PING):
                #    await aWS.ping()
                #elif (Msg.type == aiohttp.WSMsgType.PONG):
                #    await aWS.pong()
                elif (Msg.type == web.WSMsgType.close):
                    #await aWS.close(code=aWS.close_code, message=Msg.extra)
                    break
        except Exception as E:
            Log.Print(1, 'x', 'AddHandler()', aE=E)
        finally:
            self.DblWS.RecNo = 0
            RecNo = self.DblWS.FindField('WS', aWS)
            self.DblWS.RecPop(RecNo)

    async def Send(self, aWS, aData: dict):
        await aWS.send_json(aData)

    async def SendAll(self, aData: dict, aFilter: str = ''):
        self.DblWS.RecNo = 0
        for Rec in self.DblWS:
            if (aFilter == '') or (Rec.GetField('Path') == aFilter):
                await self.Send(Rec.GetField('WS'), aData)

    async def DoReplay(self, aWS, aData):
        if (self.OnReplay):
            await self.OnReplay(aWS, aData)
        else:
            await self.Send(aWS, aData)
