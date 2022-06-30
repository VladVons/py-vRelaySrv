from .FormBase import TFormBase

class TForm(TFormBase):
    Title = 'Error code'

    async def _Render(self):
        self.Data.Info = {'Code': 404, 'Path': self.Request.path}
