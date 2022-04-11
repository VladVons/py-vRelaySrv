from .FForm import TFormBase

class TForm(TFormBase):
    Title = 'Main'

    async def Render(self):
        return self._Render()
