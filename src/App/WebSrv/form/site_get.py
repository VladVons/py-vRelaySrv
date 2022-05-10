'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
Description:
'''

import time
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = 'Site get'

    async def Render(self):
        if (await self.PostToForm()):
            Download = TDownload()
            UrlDown = await Download.Get(self.Data.Url, True)
            if (UrlDown.get('Err')):
                self.Data.Output = 'Error loading %s, %s' % (self.Data.Url, UrlDown.get('Msg'))
            else:
                Status = UrlDown['Status']
                if (Status == 200):
                    Data = UrlDown['Data']
                    TimeAt = time.time()
                    if (self.Data.Path):
                        Soup = BeautifulSoup(Data, 'lxml')
                        Script = '''
                            {
                                "Product": {
                                    "Path": [%s]
                                }
                            }
                        ''' % (self.Data.Path)
                        try:
                            Scheme = TScheme(Script)
                            self.Data.Output = Scheme.Parse(Soup)
                        except Exception as E:
                            self.Data.Output = E
                    else:
                        self.Data.Output = Data

                    Arr = [
                        'Source size %s' % len(Data),
                        'Download time %.2f' % (UrlDown['Time']),
                        'Parse time %.2f' % (time.time() - TimeAt)
                    ]
                    self.Data.Info = '\n'.join(Arr)
                else:
                    self.Data.Output = 'Error loading %s. Status %s' % (self.Data.Url, Status)
        return self._Render()
