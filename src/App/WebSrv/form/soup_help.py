'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.19
License:     GNU, see LICENSE for more details
'''

import IncP.SchemeApi as SchemeApi
from IncP.ImportInf import GetClassHelp
from .FForm import TFormBase


class TForm(TFormBase):
    Title = 'Soup help'

    async def _Render(self):
        self.Data.SchemeApi = GetClassHelp(SchemeApi, SchemeApi.TSchemeApi)
