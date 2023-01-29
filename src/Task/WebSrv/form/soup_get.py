# Created: 2022.04.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import json
#
from Inc.UtilP.Misc import FilterKeyErr
from IncP.Download import GetSoupUrl
from IncP.Scheme.Utils import SoupFindParents
from .FormBase import TFormBase


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
