'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
License:     GNU, see LICENSE for more details
Description:
'''

import json
#
from .FForm import TFormBase
from IncP.Download import TDownload, CheckHost
from Inc.DB.DbList import TDbList
from IncP.DB.Db import TDbSql
from ..Api import Api
from IncP.Log import Log


class TForm(TFormBase):
    Title = 'Sites add'

    async def Render(self):
        if (await self.PostToForm()):
            if (self.Data.Sites):
                Lines = self.Data.Sites.splitlines()
                Lines = [x.strip() for x in Lines if (x)]

                Data = await Api._Send('get_sites')
                Data = Data.get('Data', {}).get('Data')
                if (Data):
                    Dbl = TDbList().DataImport(Data)
                    Diff = Dbl.GetDiff('site.url', Lines)

                    Output = []
                    Output.append('Exists:')
                    Output += list(set(Lines) - Diff[1])
                    Output.append('')

                    #Data = await TDownload().Gets(Diff[1])
                    #UrlOk = [x.get('Url') for x in Data if (x.get('Status') == 200)]
                    UrlOk = [x for x in Diff[1] if CheckHost(x)]

                    Data = await Api._Send('set_sites')
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
                        await Api._Send('add_sites', {'dbl': Dbl.DataExport()})
                else:
                    self.Data.Output = Log.Print(1, 'e', 'Cant get data from server')
        return self._Render()
