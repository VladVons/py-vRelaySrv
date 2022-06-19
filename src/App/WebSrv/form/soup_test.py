'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.08
License:     GNU, see LICENSE for more details
'''

import json
#
from .FForm import TFormBase
from IncP.Download import GetUrlSoup
from IncP.Log import Log
from IncP.Scheme import TScheme
from IncP.Utils import TJsonEncoder


class TForm(TFormBase):
    Title = 'Soup test'

    async def BtnMake(self):
        Soup = await GetUrlSoup(self.Data.Url0)
        if (not Soup):
            self.Data.Output = 'Error loading %s' % (self.Data.Url0)
            return

        try:
            Scheme = TScheme(self.Data.Script)
            Scheme.Debug = True
            Output = Scheme.Parse(Soup).GetData(['Err', 'Pipe', 'Warn'])
            self.Data.Output = json.dumps(Output,  indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
        except (json.decoder.JSONDecodeError, AttributeError) as E:
            self.Data.Output = str(E.args)
            Log.Print(1, 'x', self.Data.Output, aE=E)

    async def _Render(self):
        if (not await self.PostToForm()):
            return

        if ('BtnMake' in self.Data):
            await self.BtnMake()
