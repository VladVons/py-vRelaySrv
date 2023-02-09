# Created: 2022.02.14
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from aiohttp import web
from aiohttp_jinja2 import render_template
from wtforms import Form
#
from Inc.Conf import TDictDef
from IncP import GetInfo
from IncP.Log import Log
from ..Session import Session


class TFormBase(Form):
    Title = ''

    def __init__(self, aRequest: web.Request, aTpl: str, aData: dict = None):
        super().__init__()

        if (aData is None):
            aData = {}

        self.Request = aRequest
        self.Data = TDictDef('', aData)
        self.Info = GetInfo()
        self.Tpl = aTpl
        self.Parent = None

        if (not self.Title):
            self.Title = self.Tpl.split('.')[0]

    async def PostToForm(self):
        self.Data.clear()
        Post = await self.Request.post()
        for Key, Val in Post.items():
            if (isinstance(Val, str)):
                self.Data[Key] =  Val.strip()
        return bool(Post)

    async def Render(self) -> web.Response:
        self.process(await self.Request.post())

        await Session.Update(self.Request)
        if (Session.CheckUserAccess(self.Request.path)):
            Res = await self._Render()
            if (Res is None):
                try :
                    Res = self.RenderTemplate()
                except Exception as E:
                    Msg = 'Render(), %s %s' % (self.Tpl, E)
                    Log.Print(1, 'x', Msg, aE = E)
                    Res = self.RenderInfo(Msg)
        else:
            Msg = 'Access denied %s %s. Policy interface_allow' % (self.Request.path, Session.Data.get('UserName'))
            Res = self.RenderInfo(Msg)
        return Res

    def RenderTemplate(self):
        return render_template(self.Tpl, self.Request, {'data': self.Data, 'form': self})

    def RenderInfo(self, aMsg: str) -> web.Response:
        Data = TDictDef('', {'info': aMsg})
        return render_template('info.tpl.html', self.Request, {'data': Data, 'form': self})

    async def _Render(self):
        #print('_Render() not implemented for %s' % (self.Tpl))
        pass
