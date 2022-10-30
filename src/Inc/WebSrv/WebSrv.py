# Created: 2022.10.19
# Author:  Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import asyncio
from aiohttp import web
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_jinja2
import aiohttp_session
import jinja2
#
from Inc.Conf import TConf
from Inc.DataClass import DataClass
from .Common import FileReader


@DataClass
class TWebSrvConf():
    Port: int = 8080
    DirRoot: str = 'Task/WebSrv'
    DirForm: str = 'form'
    DirDownload: str = 'download'
    Dir3w: str = 'www'
    TplExt: str = '.tpl.html'
    ClientMaxizeFile: int = 1024**2
    ErroMiddleware: dict = {}

def CreateErroMiddleware(aOverrides):
    @web.middleware
    async def ErroMiddleware(request: web.Request, handler):
        try:
            return await handler(request)
        except web.HTTPException as E:
            Override = aOverrides.get(E.status)
            if (Override):
                return await Override(request)
            raise E
        #except Exception as E:
        #    pass
    return ErroMiddleware


class TWebSrvBase():
    def __init__(self, aSrvConf: TWebSrvConf, aConf: TConf):
        self.SrvConf = aSrvConf
        self.Conf = aConf

    async def _FormCreate(self, aRequest: web.Request, aName: str) -> web.Response:
        FormDir = f'{self.SrvConf.DirRoot}/{self.SrvConf.DirForm}'
        if (not os.path.isfile(f'{FormDir}/{aName}{self.SrvConf.TplExt}')):
            aName = 'err_code'

        for Module, Class in [(aName, 'TForm'), ('FormBase', 'TFormBase')]:
            try:
                Path = FormDir + '/' + Module
                Mod = __import__(Path.replace('/', '.'), None, None, [Class])
                TClass = getattr(Mod, Class)
                break
            except ModuleNotFoundError:
                pass
        Res = TClass(aRequest, aName + self.SrvConf.TplExt)
        Res.Parent = self
        return Res

    async def _FormCreateUser(self, aRequest: web.Request) -> web.Response:
        raise NotImplementedError()

    async def _rDownload(self, aRequest: web.Request) -> web.Response:
        Name = aRequest.match_info['Name']
        File = '%s/%s/%s' % (self.SrvConf.DirRoot, self.SrvConf.DirDownload, Name)
        if (not os.path.exists(File)):
            return web.Response(body='File %s does not exist' % (Name), status=404)

        Headers = {'Content-disposition': 'attachment; filename=%s' % (Name)}
        # pylint: disable-next=no-value-for-parameter
        return web.Response(body=FileReader(aFile=File), headers=Headers)

    async def _rForm(self, aRequest: web.Request) -> web.Response:
        Form = await self._FormCreateUser(aRequest)
        return await Form.Render()

    async def _rIndex(self, aRequest: web.Request) -> web.Response:
        Form = await self._FormCreate(aRequest, 'index')
        return await Form.Render()

    def _GetDefRoutes(self) -> list:
        return [
            web.get('/', self._rIndex),
            web.get('/form/{Name}', self._rForm),
            web.post('/form/{Name}', self._rForm),
            web.get('/download/{Name:.*}', self._rDownload)
        ]

    def CreateApp(self, aRoutes: list = None) -> web.Application:
        App = web.Application(client_max_size = self.SrvConf.ClientMaxizeFile)

        if (not aRoutes):
            aRoutes = self._GetDefRoutes()
        App.add_routes(aRoutes)

        App.router.add_static('/', f'{self.SrvConf.DirRoot}/{self.SrvConf.Dir3w}', show_index=True, follow_symlinks=True)

        aiohttp_session.setup(App, EncryptedCookieStorage(b'my 32 bytes key. qwertyuiopasdfg'))

        Middleware = CreateErroMiddleware(self.SrvConf.ErroMiddleware)
        App.middlewares.append(Middleware)

        aiohttp_jinja2.setup(App, loader=jinja2.FileSystemLoader(self.SrvConf.DirRoot + '/' + self.SrvConf.DirForm))
        return App

    async def Run(self, aApp: web.Application):
        ## pylint: disable-next=protected-access
        ## await web._run_app(App, host = '0.0.0.0', port = Port, shutdown_timeout = 60.0,  keepalive_timeout = 75.0)

        Runner = web.AppRunner(aApp)
        try:
            await Runner.setup()
            Site = web.TCPSite(Runner, host = '0.0.0.0', port = self.SrvConf.Port)
            await Site.start()
            while (True):
                await asyncio.sleep(60)
        finally:
            await Runner.cleanup()
