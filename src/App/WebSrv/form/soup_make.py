import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = "Soup make"

    def MakeOutput(self, aSoup):
        Script = {}
        Res = TScheme.ParseKeys(aSoup, Script)
        return Res
    
    async def Render(self):
        if (await self.PostToForm()):
            Download = TDownload()
            UrlDown = await Download.Get(self.Url)
            if (UrlDown.get('Err')):
                self.Output = 'Error loading %s, %s' % (self.Url, UrlDown.get('Msg')) 
            else:
                Data = UrlDown['Data']
                Status = UrlDown['Status']
                if (Status == 200):
                    Soup = BeautifulSoup(Data, 'lxml')
                    try:
                        ResScheme = self.MakeOutput(Soup)
                        self.Output = json.dumps(ResScheme, indent=4, sort_keys=True, ensure_ascii=False)
                    except (json.decoder.JSONDecodeError, AttributeError) as E:
                        self.Output = str(E.args)
                else:
                    self.Output = 'Error loading %s' % (self.Url) 
        return self._Render()
