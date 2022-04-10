import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = "Soup get"

    async def Render(self):
        Post = await self.Request.post()
        if (Post):
            self.Url = Post.get('Url').strip()
            self.Find = Post.get('Find').strip()

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
                        self.Output = ''
                        x11 = TScheme.GetParents(Soup, self.Find)
                        for x1 in x11:
                            for x in reversed(x1):
                                self.Output += json.dumps(x, ensure_ascii=False) + '\n'
                            self.Output += '\n'
                    except (json.decoder.JSONDecodeError, AttributeError) as E:
                        self.Output = str(E.args)
                else:
                    self.Output = 'Error loading %s' % (self.Url) 
        return self._Render()
