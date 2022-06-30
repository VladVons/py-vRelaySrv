'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
'''


from IncP.Download import GetSoupUrl
from IncP.Utils import FilterKeyErr
from .FormBase import TFormBase
from ..Utils import GetUrlInfo


class TForm(TFormBase):
    Title = 'Site get'

    async def _Render(self):
        if (not await self.PostToForm()) or (not self.Data.get('BtnOk')):
            return

        Data = await GetSoupUrl(self.Data.Url0)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.Output = 'Error loading %s, %s, %s' % (self.Data.Url0, Err, Data.get('Msg'))
            return

        self.Data.Output = Data.get('Data')
        Arr = GetUrlInfo(Data)
        self.Data.Info = '\n'.join(Arr)
