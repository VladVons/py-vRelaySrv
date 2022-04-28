from .FForm import TFormBase

class TForm(TFormBase):
    Title = 'Index'

    async def Render(self):
        return self._Render()
