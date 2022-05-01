'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
'''

import json
from bs4 import BeautifulSoup
#
from IncP.ApiWeb import TApiBase, TWebClient
from IncP.Scheme import TSoupScheme
from IncP.Download import TDownload
from IncP.Utils import TJsonEncoder
from IncP.Utils import GetNestedKey

class TApi(TApiBase):
    Url = {
        'get_scheme_empty':     {'param': []},
        'get_scheme_by_id':     {'param': ['id']},
        'get_scheme_test':      {'param': ['scheme']}
    }

    def __init__(self):
        self.WebClient = TWebClient()

    async def path_get_scheme_empty(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

    async def path_get_scheme_by_id(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

    async def path_get_scheme_test(self, aPath: str, aData: dict) -> dict:
        Scheme = aData['scheme']
        if (Scheme):
            Scheme = json.loads(Scheme)
            Url = GetNestedKey(Scheme, 'Product.-Info.Url')
            if (Url):
                Download = TDownload()
                UrlDown = await Download.Get(Url)
                if (UrlDown.get('Err')):
                    self.Data.Output = 'Error loading %s, %s' % (Url, UrlDown.get('Msg'))
                else:
                    Data = UrlDown['Data']
                    Soup = BeautifulSoup(Data, 'lxml')
                    return TSoupScheme.ParseKeys(Soup, Scheme)


Api = TApi()
