'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
'''

import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import GetUrlSoup
from IncP.Scheme import TSoupScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = 'Soup get'

    async def _Render(self):
        if (not await self.PostToForm()):
            return

        Soup = await GetUrlSoup(self.Data.Url0)
        if (not Soup):
            self.Data.Output = 'Error loading %s' % (self.Data.Url0)
            return

        try:
            self.Data.Output = ''
            if (self.Data.Path):
                Path = '[%s]' % self.Data.Path
                Path = json.loads(Path)
                Soup = TSoupScheme.GetItem(Soup, [Path], ({}, [], []))

            if (Soup):
                x11 = TSoupScheme.GetParents(Soup, self.Data.Find)
                for x1 in x11:
                    for x in reversed(x1):
                        self.Data.Output += json.dumps(x, ensure_ascii=False) + '\n'
                    self.Data.Output += '\n'
        except (json.decoder.JSONDecodeError, AttributeError) as E:
            self.Data.Output = str(E.args)
