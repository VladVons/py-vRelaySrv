from .FForm import TFormBase

class TForm(TFormBase):
    Title = 'About'

    async def _Render(self):
        Arr = ['%s: %s' % (Key, Val) for Key, Val in self.Info.items()]
        self.Data.Info = '<br>\n'.join(Arr)
