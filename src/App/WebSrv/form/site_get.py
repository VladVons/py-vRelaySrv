'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
'''

from bs4 import BeautifulSoup
import time
#
from .FForm import TFormBase
from IncP.Download import TDownload, THeaders
from IncP.Log import Log
from IncP.Scheme import TScheme
from IncP.Utils import FilterKeyErr


class TForm(TFormBase):
    Title = 'Site get'

    async def _Render(self):
        if (not await self.PostToForm()):
            return

        Download = TDownload()
        Download.Opt.update({'Headers': THeaders(), 'Decode': True})
        UrlDown = await Download.Get(self.Data.Url0)
        Err = FilterKeyErr(UrlDown)
        if (Err):
            self.Data.Output = 'Error loading %s, %s, %s' % (self.Data.Url0, UrlDown.get('Data'), UrlDown.get('Msg'))
            return

        Status = UrlDown['Status']
        if (Status != 200):
            self.Data.Output = 'Error loading %s. Status %s' % (self.Data.Url0, Status)
            return

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
                self.Data.Output = TScheme(Script).Parse(Soup).GetData()
                self.Data.Output.pop('Data')
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
