'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.19
License:     GNU, see LICENSE for more details
'''

from .FForm import TFormBase
from IncP.SchemeApi import TSchemeApi
from IncP.Utils import GetClassInfo


class TForm(TFormBase):
    Title = 'Soup help'

    async def _Render(self):
        self.Data.SchemeApi = GetClassInfo(TSchemeApi)
        pass
