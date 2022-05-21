'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.14
License:     GNU, see LICENSE for more details
'''

from aiohttp import web
from aiohttp_jinja2 import render_template
from wtforms import Form
import aiohttp_session
#
from IncP import Info
from IncP.Log import Log
from IncP.Utils import TDictStr


class TFormBase(Form):
    Title = ''

    def __init__(self, aRequest: web.Request, aTpl: str):
        super().__init__()

        self.Request = aRequest
        self.Data = TDictStr()
        self.Info = Info
        self.Tpl = aTpl

        if (not self.Title):
            self.Title = aTpl.split('.')[0]


    async def PostToForm(self):
        Post = await self.Request.post()
        for Key, Val in Post.items():
            self.Data[Key] = Val.strip()
        return bool(Post)

    async def Render(self) -> web.Response:
        self.Session = await aiohttp_session.get_session(self.Request)
        self.process(await self.Request.post())

        Res = await self._Render()
        if (Res is None):
            try :
                Res = render_template(self.Tpl, self.Request, {'Data': self.Data, 'Form': self})
            except Exception as E:
                Msg = 'Render(), %s %s' % (self.Tpl, E)
                Log.Print(1, 'x', Msg, aE = E)
                Res = self.RenderInfo(Msg)
        return Res

    def RenderInfo(self, aMsg: str) -> web.Response:
        Data = TDictStr({'Info': aMsg})
        return render_template('info.tpl.html', self.Request, {'Data': Data, 'Form': self})

    async def _Render(self):
        #print('_Render() not implemented for %s' % (self.Tpl))
        pass
