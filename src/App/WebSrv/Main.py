'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:

https://github.com/aio-libs/aiohttp
https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners
'''


import os
import json
from aiohttp import web, streamer
import jinja2
import aiohttp_jinja2
import base64
#
from Inc.Log import Log
from .Api import Api
from .Routes import *


@streamer
async def FileSender(writer, aFile: str):
    with open(aFile, 'rb') as F:
        Chunk = F.read(2 ** 16)
        while (Chunk):
            await writer.write(Chunk)
            Chunk = F.read(2 ** 16)

def CreateErroMiddleware(aOverrides):
    @web.middleware
    async def ErroMiddleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPException as E:
            Override = aOverrides.get(E.status)
            if (Override):
                return await Override(request)
            raise E
    return ErroMiddleware


class TWebSrv():
    def __init__(self, aConf: dict):
        self.Conf = aConf

        self.DirRoot = 'App/WebSrv'
        self.DirForm = 'form'
        self.DirDownload = 'download'
        self.Dir3w = 'www'
        self.TplExt = '.tpl.html'

    async def AuthUser(self, aRequest: web.Request) -> bool:
        if (self.Conf.get('Auth')):
            Auth = aRequest.headers.get('Authorization')
            if (Auth):
                User, Passw = base64.b64decode(Auth.split()[1]).decode().split(':')
                DBL = await self.Api.Db.AuthUser(User, Passw)
                return DBL.GetSize() > 0
        else:
            return True

    async def _LoadForm(self, aName: str, aRequest) -> web.Response:
        FormDir = '%s/%s' % (self.DirRoot, self.DirForm)
        if (not os.path.isfile('%s/%s%s' % (FormDir, aName, self.TplExt))):
            aName = 'err_404'

        for Module, Class in [(aName, 'TForm'), ('FForm', 'TFormBase')]:
            try:
                Path = FormDir + '/' + Module
                Mod = __import__(Path.replace('/', '.'), None, None, [Class])
                TClass = getattr(Mod, Class)
                break
            except ModuleNotFoundError: pass

        Obj = TClass(aRequest, aName + self.TplExt)
        return await Obj.Render()

    async def _rDownload(self, aRequest):
        Name = aRequest.match_info['Name']
        File = '%s/%s/%s' % (self.DirRoot, self.DirDownload, Name)
        if (not os.path.exists(File)):
            return web.Response(body='File %s does not exist' % (Name), status=404)
        else:
            Headers = {"Content-disposition": "attachment; filename=%s" % (Name)}
            return web.Response(body=FileSender(aFile=File), headers=Headers)

    async def _rApi(self, aRequest) -> web.Response:
        Name = aRequest.match_info.get('Name')
        Post = await aRequest.text()
        PostObj = json.loads(Post)
        Res = await Api._Send('web/' + Name, PostObj)
        Res = Res.get("Data", {})
        if (Res.get("Err", {})):
            Res = {}
        return web.json_response(Res)

    async def _rForm(self, aRequest) -> web.Response:
        Name = aRequest.match_info.get('Name')
        return await self._LoadForm(Name, aRequest)

    async def _rIndex(self, aRequest) -> web.Response:
        return await self._LoadForm('index', aRequest)

    async def Run(self):
        App = web.Application()
        App.add_routes([
            web.get("/", self._rIndex),
            web.post('/api/{Name}', self._rApi),
            web.get('/form/{Name}', self._rForm),
            web.post('/form/{Name}', self._rForm),
            web.get('/download/{Name:.*}', self._rDownload)
        ])

        App.router.add_static('/', self.DirRoot + '/' + self.Dir3w, show_index=True, follow_symlinks=True)

        Middleware = CreateErroMiddleware({
            404: rErr_404
        })
        App.middlewares.append(Middleware)

        aiohttp_jinja2.setup(App, loader=jinja2.FileSystemLoader(self.DirRoot + '/' + self.DirForm))

        #Runner = web.AppRunner(App)
        #await Runner.setup()
        #Site = web.TCPSite(Runner, '0.0.0.0', self.Conf.get('Port', 8080))
        #await Site.start()

        Port = self.Conf.get('Port', 8080)
        Log.Print(1, 'i', 'WebSrv on port %s' % (Port))
        await web._run_app(App, host = '0.0.0.0', port = Port, shutdown_timeout = 60.0,  keepalive_timeout = 75.0)
