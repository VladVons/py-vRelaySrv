from .FForm import TFormBase

class TForm(TFormBase):
    Title = 'Error page'

    async def Render(self):
        return self._Render()
