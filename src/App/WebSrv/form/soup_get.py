'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
Description:
'''

import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = 'Soup get'

    async def Render(self):
        if (await self.PostToForm()):
            Download = TDownload()
            UrlDown = await Download.Get(self.Data.Url)
            if (UrlDown.get('Err')):
                self.Data.Output = 'Error loading %s, %s' % (self.Data.Url, UrlDown.get('Msg'))
            else:
                Data = UrlDown['Data']
                Status = UrlDown['Status']
                if (Status == 200):
                    Soup = BeautifulSoup(Data, 'lxml')
                    try:
                        self.Data.Output = ''
                        if (self.Data.Path):
                            Path = '[%s]' % self.Data.Path
                            Path = json.loads(Path)
                            Soup = TScheme.GetItem(Soup, [Path], ({}, [], []))

                        if (Soup):
                            x11 = TScheme.GetParents(Soup, self.Data.Find)
                            for x1 in x11:
                                for x in reversed(x1):
                                    self.Data.Output += json.dumps(x, ensure_ascii=False) + '\n'
                                self.Data.Output += '\n'
                    except (json.decoder.JSONDecodeError, AttributeError) as E:
                        self.Data.Output = str(E.args)
                else:
                    self.Data.Output = 'Error loading %s' % (self.Data.Url)
        return self._Render()
