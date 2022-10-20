# Created: 2022.02.14
# Author:  Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from .FormBase import TFormBase


class TForm(TFormBase):
    Title = 'About'

    async def _Render(self):
        Arr = ['%s: %s' % (Key, Val) for Key, Val in self.Info.items()]
        self.Data.Info = '<br>\n'.join(Arr)
