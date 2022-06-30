'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.14
License:     GNU, see LICENSE for more details
'''


from Inc.DB.DbList import TDbList, TDbCond
from IncP.Utils import GetNestedKey, FilterKeyErr
from ..Api import Api
from .FormBase import TFormBase


class TForm(TFormBase):
    Title = 'Site list'

    async def _Render(self):
        DataApi = await Api.DefHandler('get_hand_shake')
        Err = FilterKeyErr(DataApi)
        if (Err):
            return self.RenderInfo(Err)

        DataApi = await Api.DefHandler('get_sites')
        Data = GetNestedKey(DataApi, 'Data.Data')
        if (Data):
            Dbl = TDbList().Import(Data)
            self.Data.Sites = Dbl

            Cond = TDbCond().AddFields([ ['eq', (Dbl, 'has_scheme'), True, True]])
            self.Data.CntScheme = Dbl.Clone(aCond=Cond).GetSize()
        else:
            return self.RenderInfo(DataApi.get('Data'))
