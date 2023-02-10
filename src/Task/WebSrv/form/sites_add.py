# Created: 2022.04.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from urllib.parse import urlparse
#
from Inc.Db.DbList import TDbListSafe, TDbCond, TDbSql
from Inc.Util.Obj import DeepGet
from Inc.UtilP.Misc import FilterKeyErr
from IncP.Download import CheckHost
from .FormBase import TFormBase
from ..Api import Api


class TForm(TFormBase):
    Title = 'Sites add'

    async def _Render(self):
        if (not await self.PostToForm()) and (not self.Data.sites):
            return

        DataApi = await Api.DefHandler('get_hand_shake')
        Err = FilterKeyErr(DataApi)
        if (Err):
            return self.RenderInfo(Err)

        Sites = []
        # pylint: disable-next=no-member
        Lines = self.Data.sites.splitlines()
        for Line in Lines:
            Data = urlparse(Line)
            Sites.append(Data.scheme + '://' + Data.hostname)

        DataApi = await Api.DefHandler('get_sites')
        Err = FilterKeyErr(DataApi)
        if (Err):
            self.Data.output = Err
            return

        DataDbl = DeepGet(DataApi, 'data.data')
        Dbl = TDbListSafe().Import(DataDbl)
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

        self.Data.output = '\n'.join(Output)

        if (UrlOk):
            Dbl = TDbSql(None)
            Dbl.InitList(('url', str), UrlOk)
            await Api.DefHandler('add_sites', {'dbl': Dbl.Export()})
