# Created: 2022.06.19
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# pylint: disable-next=consider-using-from-import
import Inc.Scheme.SchemeApi as SchemeApi

from Inc.Util.ModHelp import GetClassHelp
from .FormBase import TFormBase


class TForm(TFormBase):
    Title = 'Soup help'

    async def _Render(self):
        self.Data.info = {}

        ClassHelp = GetClassHelp(SchemeApi, SchemeApi.TSchemeApi)
        self.Data.info['api'] = {
            x[4]: x[3].strip()
            for x in ClassHelp
        }

        ClassHelp = GetClassHelp(SchemeApi, SchemeApi.TSchemeExt)
        self.Data.info['ext'] = {
            x[4]: x[3].strip()
            for x in ClassHelp
        }

        ClassHelp = GetClassHelp(SchemeApi, SchemeApi.TSchemeApiExt)
        ResApi = {}
        for x in ClassHelp:
            Data = getattr(SchemeApi.TSchemeApiExt, x[0])()
            ResApi[x[4]] = '\n'.join([str(d) for d in Data])
        self.Data.info['api_ext'] = ResApi

        self.Data.info['internal'] = {
           '-': 'comment\n["-find", ["div"]]',
           'as_if': '',
           'as_list': '',
           'as_dict': '',
           'pipe': 'All chains should start with pipe\n"pipe_a_": [...]'
        }
