'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.16
License:     GNU, see LICENSE for more details
'''


from aiohttp import web
import asyncio
#
from .Api import TApi
from IncP.Log import Log
from IncP.Utils import TJsonEncoder


class TScraperSrv():
    def __init__(self, aConf: dict):
        self.Conf = aConf

        #self.WebSockSrv = TWebSockServer()
        #self.WebSockSrv.OnReplay = self.cbWebSockReplay

    #async def cbWebSockReplay(self, aWS, aData: dict):
        #print('cbWebSockServer', aData)
        #await aWS.send_json(aData)

    async def cbOnStartup(self, aApp: web.Application):
        aApp['Conf'] = self.Conf

        self.Api = TApi()
        await self.Api.DbInit(self.Conf.DbAuth)
        yield
        # wait till working...

        Log.Print(1, 'i', 'cbInit(). Close connection')
        await self.Api.DbClose()

    async def _rIndex(self, aRequest: web.Request) -> web.Response:
        #await self.WebSockServer.SendAll({'hello': 111}, '/ws/test')
        if (await self.Api.AuthRequest(aRequest, self.Conf.Auth)):
            #Conf = aRequest.app.get('Conf')
            Name = aRequest.match_info.get('Name')
            Post = await aRequest.json()

            # ToDo. Test for safety
            #Res = await asyncio.shield(self.Api.Call(Name, Post))

            Res = await self.Api.Call(Name, Post)
            return web.json_response(Res, dumps=TJsonEncoder.Dumps)
        else:
            Res = {'Type': 'Err', 'Data': 'Authorization failed'}
            return web.json_response(Res, status=403)

    async def _rWebSock(self, aRequest: web.Request) -> web.WebSocketResponse:
        WS = web.WebSocketResponse()
        if (not await self.AuthUser(aRequest)):
            return WS

        await self.WebSockSrv.AddHandler(aRequest, WS)
        return WS

    async def Run(self, aSleep: int = 10):
        App = web.Application()
        #App['SomeKey'] = 'Hello'

        #App.on_startup.append(self.cbOnStartup)
        App.cleanup_ctx.append(self.cbOnStartup)

        App.add_routes([
            web.get('/web/{Name:.*}', self._rIndex),
            web.post('/web/{Name:.*}', self._rIndex),
            web.get('/ws/{Name:.*}', self._rWebSock)
        ])

        Port = self.Conf.get('Port', 8081)
        while (True):
            try:
                Log.Print(1, 'i', 'ScraperSrv on port %s' % (Port))
                await web._run_app(App, host = '0.0.0.0', port = Port, shutdown_timeout = 60.0,  keepalive_timeout = 75.0)
            except Exception as E:
                await asyncio.sleep(2)
                Log.Print(1, 'x', 'Run()', aE = E)
            await asyncio.sleep(aSleep)
