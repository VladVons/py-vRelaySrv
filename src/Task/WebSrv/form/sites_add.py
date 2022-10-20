# Created: 2022.04.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from urllib.parse import urlparse
#
from Inc.DB.DbList import TDbList, TDbCond
from Inc.Util.Obj import GetNestedKey
from IncP.DB.Db import TDbSql
from IncP.Download import CheckHost
from IncP.Utils import FilterKeyErr
from ..Api import Api
from .FormBase import TFormBase


class TForm(TFormBase):
    Title = 'Sites add'

    async def _Render(self):
        if (not await self.PostToForm()) and (not self.Data.Sites):
            return

        DataApi = await Api.DefHandler('get_hand_shake')
        Err = FilterKeyErr(DataApi)
        if (Err):
            return self.RenderInfo(Err)

        Sites = []
        Lines = self.Data.Sites.splitlines()
        for Line in Lines:
            Data = urlparse(Line)
            Sites.append(Data.scheme + '://' + Data.hostname)

        DataApi = await Api.DefHandler('get_sites')
        Err = FilterKeyErr(DataApi)
        if (Err):
            self.Data.Output = Err
            return

        DataDbl = GetNestedKey(DataApi, 'Data.Data')
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
            await Api.DefHandler('add_sites', {'dbl': Dbl.Export()})
