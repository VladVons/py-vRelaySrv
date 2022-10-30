# Created: 2021.02.26
# Author:  Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# https://github.com/aio-libs/aiohttp
# https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners


import json
from aiohttp import web
#
from Inc.Conf import TConf
from Inc.UtilP.Misc import FilterKeyErr
from Inc.WebSrv.WebSrv import TWebSrvBase, TWebSrvConf
from IncP.ApiWeb import TWebSockSrv
from IncP.Log import Log
from .Api import Api
from .Session import Session
from .Routes import rErr_404


class TWebSrv(TWebSrvBase):
    def __init__(self, aSrvConf: TWebSrvConf, aConf: TConf):
        super().__init__(aSrvConf, aConf)

        self.WebSockSrv = TWebSockSrv()
        self.WebSockSrv.Api = Api

    async def _FormCreateUser(self, aRequest: web.Request) -> web.Response: #//
        Name = aRequest.match_info.get('Name')

        await Session.Update(aRequest)
        if (not Session.Data.get('UserId')) and (Name != 'login'):
            Redirect = f'login?url={Name}'
            raise web.HTTPFound(location = Redirect)

        return await self._FormCreate(aRequest, Name)

    async def _rApi(self, aRequest: web.Request) -> web.Response:
        Name = aRequest.match_info.get('Name')
        Post = await aRequest.text()
        if (Post):
            try:
                Param = json.loads(Post)
            except Exception as E:
                return web.json_response({'Type': 'Err', 'Data': E})
        else:
            Param = {}

        if (Param.get('ws')):
            Param['ws'] = (self.WebSockSrv.DblWS, Param.get('ws'))

        Res = await Api.Call(Name, Param)
        Err = FilterKeyErr(Res)
        if (Err):
            Log.Print(1, 'e', 'TWebSrv._rApi() %s' % (Res.get('Data')))
        else:
            Res = Res.get('Data')
        return web.json_response(Res)

    async def _rWebSock(self, aRequest: web.Request) -> web.WebSocketResponse:
        if (await Api.AuthRequest(aRequest, self.Conf.Get('Auth'))):
            return await self.WebSockSrv.Handle(aRequest)

        WS = web.WebSocketResponse()
        await WS.prepare(aRequest)
        await WS.send_json({'Type': 'Err', 'Data': 'Authorization failed'})

    async def RunApp(self):
        Log.Print(1, 'i', f'WebSrv.RunApp() on port {self.SrvConf.Port}')

        self.Conf.ErroMiddleware = {
            404: rErr_404
        }

        Routes = self._GetDefRoutes()
        Routes += [
            web.post('/api/{Name}', self._rApi),
            web.get('/ws/{Name:.*}', self._rWebSock)
        ]
        App = self.CreateApp(Routes)

        await self.Run(App)
