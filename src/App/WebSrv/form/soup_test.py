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

    async def _Render(self):
        if (not await self.PostToForm()):
            return

        Soup = await GetUrlSoup(self.Data.Url)
        if (not Soup):
            self.Data.Output = 'Error loading %s' % (self.Data.Url)
            return

        try:
            Output = TScheme(self.Data.Script).Parse(Soup).GetData(['Err', 'Pipe'])
            self.Data.Output = json.dumps(Output,  indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
        except (json.decoder.JSONDecodeError, AttributeError) as E:
            self.Data.Output = str(E.args)
            Log.Print(1, 'x', self.Data.Output, aE=E)
