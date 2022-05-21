'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
Description:
'''

from urllib.parse import urlparse
#
from ..Api import Api
from .FForm import TFormBase
from Inc.DB.DbList import TDbList, TDbCond
from IncP.DB.Db import TDbSql
from IncP.Download import TDownload, CheckHost
from IncP.Log import Log
from IncP.Utils import GetNestedKey


class TForm(TFormBase):
    Title = 'Sites add'

    async def _Render(self):
        if (not await self.PostToForm()) and (not self.Data.Sites):
            return

        DataApi = await Api.WebClient.Send('web/get_hand_shake')
        if (GetNestedKey(DataApi, 'Type') == 'Err'):
            return self.RenderInfo(DataApi.get('Data'))

        Sites = []
        Lines = self.Data.Sites.splitlines()
        for Line in Lines:
            Data = urlparse(Line)
            Sites.append(Data.scheme + '://' + Data.hostname)

        DataApi = await Api.WebClient.Send('web/get_sites')
        DataDbl = GetNestedKey(DataApi, 'Data.Data')
        if (not DataDbl):
            self.Data.Output = Log.Print(1, 'e', 'Cant get data from server')
            return

        Dbl = TDbList().Import(DataDbl)
        Diff = Dbl.GetDiff('url', Sites)

        Cond = TDbCond().AddFields([ ['eq', (Dbl, 'has_scheme'), True, True]])
        DblScheme = Dbl.Clone(aCond=Cond)

        Output = []
        Output.append('Count:')
        Output.append('%s / %s (scheme)' % (Dbl.GetSize(), DblScheme.GetSize()))
        Output.append('')

        Output.append('Exists:')
        Output += list(set(Sites) - Diff[1])
        Output.append('')

        #Data = await TDownload().Gets(Diff[1])
        #UrlOk = [x.get('Url') for x in Data if (x.get('Status') == 200)]
        UrlOk = [x for x in Diff[1] if CheckHost(x)]

        Output.append('New:')
        Output += UrlOk
        Output.append('')

        Output.append('Bad:')
        Output += list(Diff[1] - set(UrlOk))
        Output.append('')

        self.Data.Output = '\n'.join(Output)

        if (UrlOk):
            Dbl = TDbSql(None)
            Dbl.InitList(('url', str), UrlOk)
            await Api.WebClient.Send('web/add_sites', {'dbl': Dbl.Export()})
