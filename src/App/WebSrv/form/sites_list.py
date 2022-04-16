'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.14
License:     GNU, see LICENSE for more details
Description:
'''


from .FForm import TFormBase
from IncP.Log import Log
from ..Api import Api
from Inc.DB.DbList import TDbList

class TForm(TFormBase):
    Title = "Site list"

    async def Render(self):
        Data = await Api._Send('get_sites')
        Data = Data.get('Data', {}).get('Data')
        if (Data):
            self.Data.Sites = TDbList().DataImport(Data)
        return self._Render()