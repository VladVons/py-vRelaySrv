'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.19
License:     GNU, see LICENSE for more details
'''

import IncP.SchemeApi as SchemeApi
from IncP.SchemeApi import SchemeApiExt
from IncP.ImportInf import GetClassHelp
from .FForm import TFormBase


class TForm(TFormBase):
    Title = 'Soup help'

    async def _Render(self):
        self.Data.Info = {}

        Data = GetClassHelp(SchemeApi, SchemeApi.TSchemeApi)
        self.Data.Info['Api'] = {
            x[4]: x[3].strip()
            for x in Data
        }

        self.Data.Info['Macros'] = {
            Key: '\n'.join([str(x) for x in Val])
            for Key, Val in SchemeApiExt.items()
        }

        self.Data.Info['Internal'] = {
           '-': 'comment\n["-find", ["div"]]',
           'as_if': '',
           'as_list': '',
           'as_dict': '',
           '["var_set", ["$Price"]]': 'set current chain value to $Price variable',
           '["var_get", ["$Price"]]': 'get $Price variable into chain',
           '["$root"]': 'get root object',
           'Pipe': 'All chains should start with Pipe\n"Pipe": [...]'
        }
