# Created: 2022.02.14
# Author:  Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from .FormBase import TFormBase

class TForm(TFormBase):
    Title = 'Error code'

    async def _Render(self):
        self.Data.Info = {'Code': 404, 'Path': self.Request.path}
