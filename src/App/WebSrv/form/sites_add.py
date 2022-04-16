'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
Description:
'''

import json
#
from .FForm import TFormBase
from IncP.Download import TDownload
from Inc.DB.DbList import TDbList
from ..Api import Api
from IncP.Log import Log


class TForm(TFormBase):
    Title = 'Sites add'

    async def Render(self):
        if (await self.PostToForm()):
            if (self.Data.Sites):
                Data = await Api._Send('get_sites')
                Data = Data.get('Data', {}).get('Data')
                if (Data):
                    Dbl = TDbList().DataImport(Data)
                    Lines = self.Data.Sites.splitlines()
                    Diff = Dbl.GetDiff('site.url', Lines)
                    Download = TDownload()
                    Data = await Download.Gets(Diff[1])
                    UrlOk = [x.get('Url') for x in Data if (x.get('Status') == 200)]

                    self.Data.Output = '\n'.join(UrlOk)
                else:
                    self.Data.Output = Log.Print(1, 'e', 'Cant get data from server')
        return self._Render()
