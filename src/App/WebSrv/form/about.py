'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.02.14
License:     GNU, see LICENSE for more details
'''

from .FForm import TFormBase


class TForm(TFormBase):
    Title = 'About'

    async def _Render(self):
        Arr = ['%s: %s' % (Key, Val) for Key, Val in self.Info.items()]
        self.Data.Info = '<br>\n'.join(Arr)
