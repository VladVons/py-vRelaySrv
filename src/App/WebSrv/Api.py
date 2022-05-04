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
from Inc.DB.DbList import TDbList


class TApi(TApiBase):
    def __init__(self):
        super().__init__()

        self.Url = {
            'get_scheme_empty':         {'param': ['cnt']},
            'get_scheme_not_empty':     {'param': ['cnt']},
            'get_scheme':               {'param': ['id']},
            'get_scheme_find':          {'param': ['url']},
            'get_scheme_test':          {'param': ['scheme']},
            'set_scheme':               {'param': ['id', 'scheme']}
        }

        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

    async def DefHandler(self, aPath: str, aData: dict) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

    async def path_get_scheme_find(self, aPath: str, aData: dict) -> dict:
        Data = await self.WebClient.Send('web/get_scheme_not_empty', {'cnt': 100})
        DataDbL = GetNestedKey(Data, 'Data.Data')
        if (DataDbL):
            DbL = TDbList().Import(DataDbL)

            Url = aData.get('url')
            Download = TDownload()
            UrlDown = await Download.Get(Url)
            if (UrlDown.get('Err')):
                Res = {'Err': 'Error loading %s, %s' % (Url, UrlDown.get('Msg'))}
            else:
                Arr = []
                Soup = BeautifulSoup(UrlDown['Data'], 'lxml')
                for Rec in DbL:
                    Scheme = json.loads(Rec.GetField('scheme'))
                    Parsed = TSoupScheme.ParseKeys(Soup, Scheme)
                    if (Parsed['Product'][0]):
                        Arr.append((Rec.GetField('url'), Parsed['Product'][0]))
                Res = {'Data': Arr}
        else:
            Res = {'Err': 'Error getting scheme'}
        return Res

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
