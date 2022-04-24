'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.14
License:     GNU, see LICENSE for more details
Description:
'''


from .FForm import TFormBase
from ..Api import Api
from Inc.DB.DbList import TDbList

class TForm(TFormBase):
    Title = 'Site list'

    async def Render(self):
        DataA = await Api._Send('web/get_sites')
        Data = DataA.get('Data', {}).get('Data')
        if (Data):
            self.Data.Sites = TDbList().Import(Data)
        return self._Render()
