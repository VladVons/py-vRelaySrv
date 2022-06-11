'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.14
License:     GNU, see LICENSE for more details
'''


from ..Api import Api
from .FForm import TFormBase
from Inc.DB.DbList import TDbList, TDbCond
from IncP.Utils import GetNestedKey

class TForm(TFormBase):
    Title = 'Site list'

    async def _Render(self):
        DataApi = await Api.DefHandler('get_hand_shake')
        if (GetNestedKey(DataApi, 'Type') == 'Err'):
            return self.RenderInfo(DataApi.get('Data'))

        DataApi = await Api.DefHandler('get_sites')
        Data = GetNestedKey(DataApi, 'Data.Data')
        if (Data):
            Dbl = TDbList().Import(Data)
            self.Data.Sites = Dbl

            Cond = TDbCond().AddFields([ ['eq', (Dbl, 'has_scheme'), True, True]])
            self.Data.CntScheme = Dbl.Clone(aCond=Cond).GetSize()
        else:
            return self.RenderInfo(DataApi.get('Data'))
