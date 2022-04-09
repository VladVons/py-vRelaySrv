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
        Post = await self.Request.post()
        if (Post):
            self.Url = Post.get('Url').strip()
            self.Script = Post.get('Script').strip()

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
                        Script = json.loads(self.Script)
                        ResScheme = TScheme.ParseKeys(Soup, Script)
                        self.Output = json.dumps(ResScheme,  indent=4, sort_keys=True, ensure_ascii=False)
                    except (json.decoder.JSONDecodeError, AttributeError) as E:
                        self.Output = str(E.args)
                else:
                    self.Output = 'Error loading %s' % (self.Url) 
        return self._Render()
