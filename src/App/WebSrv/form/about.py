from .FForm import TFormBase

class TForm(TFormBase):
    Title = 'About'

    async def _Render(self):
        self.Info = {'AppVer': '0.0.1'}
