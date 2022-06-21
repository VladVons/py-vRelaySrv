'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
'''

import json
#
from .FForm import TFormBase
from IncP.Download import GetSoupUrl
from IncP.Log import Log
from IncP.Scheme import TSoupScheme, SoupFindParents
from IncP.Utils import FilterKeyErr


class TForm(TFormBase):
    Title = 'Soup get'

    async def _Render(self):
        if (not await self.PostToForm()) or (not self.Data.get('BtnOk')):
            return

        Url = self.Data.Url0
        Data = await GetSoupUrl(Url)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.Output = 'Error loading %s, %s' % (Url, Err)
            return

        try:
            self.Data.Output = ''
            if (self.Data.Path):
                Path = '[%s]' % self.Data.Path
                Path = json.loads(Path)

            x11 = SoupFindParents(Data.get('Soup'), self.Data.Find)
            for x1 in x11:
                for x in reversed(x1):
                    self.Data.Output += json.dumps(x, ensure_ascii=False) + '\n'
                self.Data.Output += '\n'
        except (json.decoder.JSONDecodeError, AttributeError) as E:
            self.Data.Output = str(E.args)
