import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = "Soup test"

    async def Render(self):
        if (await self.PostToForm()):
            Download = TDownload()
            UrlDown = await Download.Get(self.Data.Url)
            if (UrlDown.get('Err')):
                self.Data.Output = 'Error loading %s, %s' % (self.Data.Url, UrlDown.get('Msg')) 
            else:
                Data = UrlDown['Data']
                Status = UrlDown['Status']
                if (Status == 200):
                    Soup = BeautifulSoup(Data, 'lxml')
                    try:
                        Script = json.loads(self.Data.Script)
                        ResScheme = TScheme.ParseKeys(Soup, Script)
                        self.Data.Output = json.dumps(ResScheme,  indent=2, sort_keys=True, ensure_ascii=False)
                    except (json.decoder.JSONDecodeError, AttributeError) as E:
                        self.Data.Output = str(E.args)
                else:
                    self.Data.Output = 'Error loading %s' % (self.Data.Url) 
        return self._Render()
