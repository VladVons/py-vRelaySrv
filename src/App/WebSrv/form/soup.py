from .FForm import TFormBase

class TForm(TFormBase):
    Title = "Check soup"

    async def Render(self):
        Data = await self.Request.post()
        return self._Render()
