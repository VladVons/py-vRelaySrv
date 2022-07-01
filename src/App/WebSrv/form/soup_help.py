'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.19
License:     GNU, see LICENSE for more details
'''

import IncP.SchemeApi as SchemeApi
from IncP.ImportInf import GetClassHelp
from .FormBase import TFormBase


class TForm(TFormBase):
    Title = 'Soup help'

    async def _Render(self):
        self.Data.Info = {}

        ClassHelp = GetClassHelp(SchemeApi, SchemeApi.TSchemeApi)
        self.Data.Info['Api'] = {
            x[4]: x[3].strip()
            for x in ClassHelp
        }

        ClassHelp = GetClassHelp(SchemeApi, SchemeApi.TSchemeApiExt)
        ApiExt = {}
        for x in ClassHelp:
            Data = getattr(SchemeApi.TSchemeApiExt, x[0])()
            ApiExt[x[4]] = '\n'.join([str(d) for d in Data])
        self.Data.Info['ApiExt'] = ApiExt


        self.Data.Info['Internal'] = {
           '-': 'comment\n["-find", ["div"]]',
           'as_if': '',
           'as_list': '',
           'as_dict': '',
           '["var_set", ["$Price"]]': 'set current chain value to $Price variable',
           '["var_get", ["$root"]]': 'get root chain',
           'Pipe': 'All chains should start with Pipe\n"PipeA": [...]'
        }
