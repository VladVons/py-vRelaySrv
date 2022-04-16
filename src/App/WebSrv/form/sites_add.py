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
from IncP.Log import Log


class TForm(TFormBase):
    Title = "Sites add"

    async def Render(self):
        if (await self.PostToForm()):
            if (self.Data.Sites):
                Lines = self.Data.Sites.splitlines()
                Download = TDownload()
                Data = await Download.Gets(Lines)
                self.Data.Output = self.Data.Sites
        return self._Render()
