'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.08
License:     GNU, see LICENSE for more details
'''

import json
#
from IncP.Download import GetSoupUrl
from IncP.Log import Log
from IncP.Scheme import TScheme
from IncP.Utils import TJsonEncoder, FormatJsonStr, FilterKeyErr
from .FForm import TFormBase
from ..Utils import GetUrlInfo


class TForm(TFormBase):
    Title = 'Soup test'

    async def Load(self):
        Data = await GetSoupUrl(self.Data.Url0)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.Output = 'Error loading %s, %s' % (self.Data.Url0, Err)
        else:
            return Data

    async def BtnMake(self):
        Data = await self.Load()
        if (not Data):
            return

        try:
            if (r'\n' in self.Data.Script):
                self.Data.Script = self.Data.Script.encode().decode('unicode_escape').strip('"\n\r')

            Scheme = TScheme(self.Data.Script)
            Scheme.Debug = True
            Output = Scheme.Parse(Data.get('Soup')).GetData(['Err', 'Pipe', 'Warn'])
            self.Data.Output = json.dumps(Output,  indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
            if (Scheme.IsJson()):
                self.Data.Script = FormatJsonStr(self.Data.Script)
        except (json.decoder.JSONDecodeError, AttributeError) as E:
            self.Data.Output = str(E.args)
            Log.Print(1, 'x', self.Data.Output, aE=E)

    async def BtnInfo(self):
        Data = await self.Load()
        if (Data):
            Arr = GetUrlInfo(Data)
            self.Data.Output = '\n'.join(Arr) + '\n'

    async def BtnSource(self):
        Data = await self.Load()
        if (Data):
            self.Data.Output = Data.get('Data')

    async def _Render(self):
        if (not await self.PostToForm()):
            return

        if ('BtnMake' in self.Data):
            await self.BtnMake()
        elif ('BtnInfo' in self.Data):
            await self.BtnInfo()
        elif ('BtnSource' in self.Data):
            await self.BtnSource()
