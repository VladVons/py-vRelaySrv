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
class TSrvConf():
    client_max_file_size: int = 1024**2
    host: str = '0.0.0.0'
    port: int = 8080


class TWebSrvConf(TSrvConf):
    dir_3w: str = 'www'
    dir_download: str = 'download'
    dir_form: str = 'form'
    dir_root: str = 'Task/WebSrv'
    tpl_ext: str = '.tpl.html'


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


class TSrvBase():
    def __init__(self, aSrvConf: TSrvConf):
        self._SrvConf = aSrvConf

    def _GetDefRoutes(self) -> list:
        raise NotImplementedError()

    @property
    def SrvConf(self):
        return self._SrvConf

    def CreateApp(self, aRoutes: list = None, aErroMiddleware: dict = None) -> web.Application:
        App = web.Application(client_max_size = self._SrvConf.client_max_file_size)

        if (not aRoutes):
            aRoutes = self._GetDefRoutes()
        App.add_routes(aRoutes)

        if (aErroMiddleware):
            Middleware = CreateErroMiddleware(aErroMiddleware)
            App.middlewares.append(Middleware)

        aiohttp_session.setup(App, EncryptedCookieStorage(b'my 32 bytes key. qwertyuiopasdfg'))
        return App

    async def Run(self, aApp: web.Application):
        ## pylint: disable-next=protected-access
        ## await web._run_app(App, host = '0.0.0.0', port = 8080, shutdown_timeout = 60.0,  keepalive_timeout = 75.0)

        Runner = web.AppRunner(aApp)
        try:
            await Runner.setup()
            Site = web.TCPSite(Runner, host = self._SrvConf.host, port = self._SrvConf.port)
            await Site.start()
            while (True):
                await asyncio.sleep(60)
        finally:
            await Runner.cleanup()

class TWebSrvBase(TSrvBase):
    def __init__(self, aSrvConf: TWebSrvConf, aConf: TConf):
        super().__init__(aSrvConf)
        self.Conf = aConf
        self.DefPage = 'info'

    async def _FormCreate(self, aRequest: web.Request, aName: str) -> web.Response:
        FormDir = f'{self._SrvConf.dir_root}/{self._SrvConf.dir_form}'

        File = f'{FormDir}/{aName}{self._SrvConf.tpl_ext}'
        NameTpl = aName if os.path.isfile(File) else self.DefPage

        File = f'{FormDir}/{aName}.py'
        NameMod = aName if os.path.isfile(File) else self.DefPage

        for Module, Class in [(NameMod, 'TForm'), ('FormBase', 'TFormBase')]:
            try:
                Path = FormDir + '/' + Module
                Mod = __import__(Path.replace('/', '.'), None, None, [Class])
                TClass = getattr(Mod, Class)
                break
            except ModuleNotFoundError:
                pass
        Res = TClass(aRequest, NameTpl + self._SrvConf.tpl_ext)
        Res.Parent = self
        return Res

    async def _FormCreateUser(self, aRequest: web.Request) -> web.Response:
        raise NotImplementedError()

    async def _rDownload(self, aRequest: web.Request) -> web.Response:
        Name = aRequest.match_info['name']
        File = '%s/%s/%s' % (self._SrvConf.dir_root, self._SrvConf.dir_download, Name)
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
            web.get('/form/{name}', self._rForm),
            web.post('/form/{name}', self._rForm),
            web.get('/download/{name:.*}', self._rDownload)
        ]

    def CreateApp(self, aRoutes: list = None, aErroMiddleware: dict = None) -> web.Application:
        App = super().CreateApp(aRoutes, aErroMiddleware)

        App.router.add_static('/', f'{self._SrvConf.dir_root}/{self._SrvConf.dir_3w}', show_index=True, follow_symlinks=True)
        aiohttp_jinja2.setup(App, loader=jinja2.FileSystemLoader(self._SrvConf.dir_root + '/' + self._SrvConf.dir_form))
        return App
