'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.14
License:     GNU, see LICENSE for more details
'''

from aiohttp import web
from aiohttp_jinja2 import render_template
from wtforms import Form
import aiohttp_session
import re
#
from Inc.Conf import TDictDef
from IncP import Info
from IncP.Log import Log


class TFormBase(Form):
    Title = ''

    def __init__(self, aRequest: web.Request, aTpl: str):
        super().__init__()

        self.Request = aRequest
        self.Data = TDictDef('')
        self.Info = Info
        self.Tpl = aTpl

        if (not self.Title):
            self.Title = aTpl.split('.')[0]

    async def PostToForm(self):
        self.Data.clear()
        Post = await self.Request.post()
        for Key, Val in Post.items():
            self.Data[Key] =  Val.strip()
        return bool(Post)

    @staticmethod
    def _CheckAccess(aUrl: str, aUrls: list):
        if (aUrls):
            for x in aUrls:
                try:
                    if (x.strip()) and (not x.startswith('-')) and (re.match(x, aUrl)):
                        return True
                except Exception as E:
                    Log.Print(1, 'e', 'CheckAccess()', aE = E)
                    return False
        return False

    def CheckAccess(self, aUrl: str):
        Grant = ['/$', '/form/login', '/form/about']
        Allow = self.Session.get('UserConf', {}).get('interface_allow', '').split() + Grant
        Deny = self.Session.get('UserConf', {}).get('interface_deny', '').split()
        return (self._CheckAccess(aUrl, Allow)) and (not self._CheckAccess(aUrl, Deny))

    async def Render(self) -> web.Response:
        self.Session = await aiohttp_session.get_session(self.Request)
        self.process(await self.Request.post())

        if (self.CheckAccess(self.Request.path)):
            Res = await self._Render()
            if (Res is None):
                try :
                    Res = render_template(self.Tpl, self.Request, {'Data': self.Data, 'Form': self})
                except Exception as E:
                    Msg = 'Render(), %s %s' % (self.Tpl, E)
                    Log.Print(1, 'x', Msg, aE = E)
                    Res = self.RenderInfo(Msg)
        else:
            Msg = 'Access denied for %s. Policy interface_allow' % (self.Request.path)
            Res = self.RenderInfo(Msg)
        return Res

    def RenderInfo(self, aMsg: str) -> web.Response:
        Data = TDictDef('', {'Info': aMsg})
        return render_template('info.tpl.html', self.Request, {'Data': Data, 'Form': self})

    async def _Render(self):
        #print('_Render() not implemented for %s' % (self.Tpl))
        pass
