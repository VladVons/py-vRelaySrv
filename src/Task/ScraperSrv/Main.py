# Created: 2022.03.16
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from aiohttp import web
#
from Inc.Misc.Misc import TJsonEncoder
from Inc.Sql.ADb import TDbAuth
from Inc.SrvWeb.SrvApi import TWebSockSrv
from Inc.SrvWeb.SrvBase import TSrvBase, TSrvConf
from IncP.Log import Log
from .Api import Api


class TScraperSrv(TSrvBase):
    def __init__(self, aConf: dict):
        SrvConf = aConf.get('srv_conf')
        DbConf = aConf['db_conf']['auth']
        super().__init__(TSrvConf(**SrvConf))
        self._DbConf = TDbAuth(**DbConf)
        self.Auth = aConf.get('auth')

        self.WebSockSrv = TWebSockSrv()
        #self.WebSockSrv.Api = Api

    def _GetDefRoutes(self) -> list:
        return [
            web.get('/web/{Name:.*}', self._rWebApi),
            web.post('/web/{Name:.*}', self._rWebApi),
            web.get('/ws/{Name:.*}', self._rWebSock)
        ]

    @staticmethod
    async def _Err_404(aRequest: web.Request) -> web.Response:
        Data = {'err': f'unknown path {aRequest.path}'}
        return web.json_response(Data, status = 404)


    async def _cbOnStartup(self, aApp: web.Application):
        aApp['conf'] = self.Conf

        await Api.DbInit(self._DbConf)
        yield
        # wait till working...

        Log.Print(1, 'i', '_cbOnStartup(). Close connection')
        await Api.DbClose()

    async def _rWebApi(self, aRequest: web.Request) -> web.Response:
        #await self.WebSockServer.SendAll({'hello': 111}, '/ws/test')
        if (await Api.AuthRequest(aRequest, self.Conf.Auth)):
            #Conf = aRequest.app.get('conf')
            Name = aRequest.match_info.get('name')
            Post = await aRequest.json()

            # ToDo. Test for safety
            #Res = await asyncio.shield(Api.Call(Name, Post))

            Res = await Api.Call(Name, Post)
            return web.json_response(Res, dumps=TJsonEncoder.Dumps)

        Res = {'type': 'err', 'data': 'Authorization failed'}
        return web.json_response(Res, status=403)

    async def _rWebSock(self, aRequest: web.Request) -> web.WebSocketResponse:
        if (await Api.AuthRequest(aRequest, self.Auth)):
            return await self.WebSockSrv.Handle(aRequest)

        WS = web.WebSocketResponse()
        await WS.prepare(aRequest)
        await WS.send_json({'type': 'err', 'data': 'Authorization failed'})

    async def RunApp(self):
        Log.Print(1, 'i', f'TScraperSrv.RunApp() on port {self._SrvConf.port}')

        App = self.CreateApp(aErroMiddleware = {404: self._Err_404})
        App.cleanup_ctx.append(self._cbOnStartup)

        await self.Run(App)
