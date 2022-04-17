'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.14
License:     GNU, see LICENSE for more details
Description:
'''


import aiohttp_jinja2
#
from IncP.Utils import TDictStr


class TFormBase():
    Title = 'Title'

    def __init__(self, aRequest, aTpl: str):
        self.Request = aRequest
        self.Tpl = aTpl
        self.Data = TDictStr()

    async def PostToForm(self):
        Post = await self.Request.post()
        for Key, Val in Post.items():
            self.Data[Key] = Val.strip()
        return bool(Post)

    def _Render(self):
        return aiohttp_jinja2.render_template(self.Tpl, self.Request, {'Data': self.Data, 'Form': self})

    async def Render(self):
        return self._Render()
