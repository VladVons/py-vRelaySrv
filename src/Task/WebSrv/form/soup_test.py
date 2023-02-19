# Created: 2022.04.08
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import json
#
from Inc.Misc.Misc import TJsonEncoder, FormatJsonStr, FilterKeyErr
from IncP.Download import GetSoupUrl
from IncP.Log import Log
from IncP.Scheme.Scheme import TScheme
from .FormBase import TFormBase
from ..Utils import GetUrlInfo, GetApiHelp


class TForm(TFormBase):
    Title = 'Soup test'

    async def Load(self):
        Data = await GetSoupUrl(self.Data.url0)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.output = 'Error loading %s, %s' % (self.Data.url0, Err)
        else:
            return Data

    async def BtnMake(self):
        Data = await self.Load()
        if (not Data):
            return

        try:
            if (r'\n' in self.Data.script):
                self.Data.script = self.Data.script.encode().decode('unicode_escape').strip('"\n\r')

            Scheme = TScheme(self.Data.script)
            Scheme.Debug = True
            Output = Scheme.Parse(Data.get('soup')).GetData(['err', 'pipe', 'warn'])
            Unknown = [x for x in Output.get('err', []) if 'unknown' in x]
            if (Unknown):
                Output['help'] = GetApiHelp()

            self.Data.output = json.dumps(Output,  indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
            if (Scheme.IsJson()):
                self.Data.script = FormatJsonStr(self.Data.script)
        except (json.decoder.JSONDecodeError, AttributeError) as E:
            self.Data.output = str(E.args)
            Log.Print(1, 'x', self.Data.output, aE=E)

    async def BtnInfo(self):
        Data = await self.Load()
        if (Data):
            Arr = GetUrlInfo(Data)
            self.Data.output = '\n'.join(Arr) + '\n'

    async def BtnSource(self):
        Data = await self.Load()
        if (Data):
            self.Data.output = Data.get('data')

    async def _Render(self):
        if (not await self.PostToForm()):
            return

        if ('btn_make' in self.Data):
            await self.BtnMake()
        elif ('btn_info' in self.Data):
            await self.BtnInfo()
        elif ('btn_source' in self.Data):
            await self.BtnSource()
