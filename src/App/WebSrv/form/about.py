from .FForm import TFormBase

class TForm(TFormBase):
    Title = 'About'

    async def Render(self):
        self.Info = {'AppVer': '0.0.1'}
        return self._Render()
