import json
import aiohttp
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


class TForm(TFormBase):
    Title = "Check soup"

    async def Render(self):
        Post = await self.Request.post()
        if (Post):
            self.Url = Post.get('url')
            self.Script = Post.get('script')

            Download = TDownload()
            try:
                UrlData = await Download.Get(self.Url)
            except (aiohttp.ClientConnectorError, aiohttp.ClientError, aiohttp.InvalidURL) as E:
                Log.Print(1, 'x', '_Worker(). %s' % (self.Url), aE = E)

            if (UrlData):
                Data, Status = UrlData
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
