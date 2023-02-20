# Created: 2021.02.26
# Author:  Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# https://github.com/aio-libs/aiohttp
# https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners


import json
from aiohttp import web
#
from Inc.Conf import TConf
from Inc.Misc.Misc import FilterKeyErr
from Inc.WebSrv.WebSrv import TWebSrvBase, TWebSrvConf
from Inc.WebSrv.WebApi import TWebSockSrv
from IncP.Log import Log
from .Api import Api
from .Session import Session
from .form.info import TForm


class TWebSrv(TWebSrvBase):
    def __init__(self, aSrvConf: TWebSrvConf, aConf: TConf):
        super().__init__(aSrvConf, aConf)

        self.WebSockSrv = TWebSockSrv()
        self.WebSockSrv.Api = Api

    async def _FormCreateUser(self, aRequest: web.Request) -> web.Response: #//
        Name = aRequest.match_info.get('name')

        await Session.Update(aRequest)
        if (not Session.Data.get('user_id')) and (Name != 'login'):
            Redirect = f'login?url={Name}'
            raise web.HTTPFound(location = Redirect)

        return await self._FormCreate(aRequest, Name)

    @staticmethod
    async def _Err_404(aRequest: web.Request):
        #https://docs.aiohttp.org/en/stable/web_advanced.html
        #Routes = web.RouteTableDef()

        Form = TForm(aRequest, 'info.tpl.html')
        Form.Data['info'] = 'Page not found'
        Res = await Form.Render()
        Res.set_status(404, Form.Data['info'])
        return Res

    async def _rApi(self, aRequest: web.Request) -> web.Response:
        Name = aRequest.match_info.get('name')
        Post = await aRequest.text()
        if (Post):
            try:
                Param = json.loads(Post)
            except Exception as E:
                return web.json_response({'type': 'err', 'data': E})
        else:
            Param = {}

        if (Param.get('ws')):
            Param['ws'] = (self.WebSockSrv.DblWS, Param.get('ws'))

        Res = await Api.Call(Name, Param)
        Err = FilterKeyErr(Res)
        if (Err):
            Log.Print(1, 'e', 'TWebSrv._rApi() %s' % (Res.get('data')))
        else:
            Res = Res.get('data')
        return web.json_response(Res)

    async def _rWebSock(self, aRequest: web.Request) -> web.WebSocketResponse:
        if (await Api.AuthRequest(aRequest, self.Conf.Get('auth'))):
            return await self.WebSockSrv.Handle(aRequest)

        WS = web.WebSocketResponse()
        await WS.prepare(aRequest)
        await WS.send_json({'type': 'err', 'data': 'Authorization failed'})

    async def RunApp(self):
        Log.Print(1, 'i', f'WebSrv.RunApp() on port {self.SrvConf.Port}')

        ErroMiddleware = {
            404: self._Err_404
        }

        Routes = self._GetDefRoutes()
        Routes += [
            web.post('/api/{Name}', self._rApi),
            web.get('/ws/{Name:.*}', self._rWebSock)
        ]
        App = self.CreateApp(Routes, ErroMiddleware)

        await self.Run(App)
