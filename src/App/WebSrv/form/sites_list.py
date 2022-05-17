'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.14
License:     GNU, see LICENSE for more details
Description:
'''


from .FForm import TFormBase
from ..Api import Api
from Inc.DB.DbList import TDbList, TDbCond
from IncP.Utils import GetNestedKey

class TForm(TFormBase):
    Title = 'Site list'

    async def _Render(self):
        DataA = await Api.WebClient.Send('web/get_sites')
        Data = GetNestedKey(DataA, 'Data.Data')
        if (Data):
            Dbl = TDbList().Import(Data)
            self.Data.Sites = Dbl

            Cond = TDbCond().AddFields([ ['eq', (Dbl, 'has_scheme'), True, True]])
            self.Data.CntScheme = Dbl.Clone(aCond=Cond).GetSize()
