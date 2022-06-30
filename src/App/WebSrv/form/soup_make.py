'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
'''

import asyncio
import datetime
import json
#
from IncP.Download import GetSoupUrl
from IncP.Scheme import TScheme
from IncP.Utils import TJsonEncoder, FormatJsonStr, FilterKey, FilterKeyErr
from .FormBase import TFormBase
from ..Api import Api
from ..Session import Session
from ..Utils import GetUrlInfo


_FieldPrefix = 'script_'


class TForm(TFormBase):
    Title = 'Soup make'

    def StripDataLines(self, aKeys: list):
        for Key in aKeys:
            Val = self.Data[Key]
            if (Val):
                Arr = [Line.strip() for Line in Val.splitlines()]
                self.Data[Key] = '\n'.join(Arr).rstrip(',')

    def Compile(self, aUrls: list) -> tuple:
        Err = []
        try:
            json.loads('[%s]' % self.Data.Pipe)
            json.loads('{%s}' % self.Data.Var)
        except ValueError as E:
            Err.append('Err: %s\n' % E.args)

        Items = []
        for Key, Val in self.Data.items():
            if (Key.startswith(_FieldPrefix)) and (Val) and (not Val.startswith('-')):
                Key = Key.replace(_FieldPrefix, '')
                try:
                    json.loads(f'[{Val}]')
                except ValueError as E:
                    Err.append('%s: %s\n' % (Key, E.args))

                Items.append('''
                            "%s": [
                                %s
                            ]''' % (Key, Val))
        Urls = ',\n'.join('"%s"' % x for x in aUrls)
        ScriptStr = '''
            {
                "Product": {
                    "Info": {
                        "Author": "%s",
                        "Date": "%s",
                        "Url": [
                            %s
                        ],
                        "Comment": "%s"
                    },
                    "Var": {
                        %s
                    },
                    "Pipe": [
                        %s,
                        ["as_dict", {
                            %s
                        }]
                    ]
                }
            }
        ''' % (
                Session.Data.get('UserName'),
                datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                Urls,
                self.Data.Comment,
                self.Data.Var,
                self.Data.Pipe,
                ','.join(Items)
            )

        return (FormatJsonStr(ScriptStr), '\n'.join(Err))

    def CompileUrl(self):
        Urls = [
            Val
            for Key, Val in self.Data.items()
            if (Val and Key.startswith('Url'))
        ]

        FieldsScript = [Key for Key in self.Data if Key.startswith(_FieldPrefix)] + ['Pipe']
        self.StripDataLines(FieldsScript)
        return (self.Compile(Urls), Urls)

    async def BtnMake(self):
        if (self.Data.Admin):
            if (self.Data.get('BtnModerateFlag') == 'True'):
                #ScriptOrig = json.loads(self.Data.Script)
                pass
        else:
            if (self.Data.get('BtnSaveFlag') == 'disabled'):
                self.Data.BtnSaveDisabled = 'disabled'

        (Script, Err), Urls = self.CompileUrl()
        if (Err):
            self.Data.Output = Err
            return

        self.Data.Script = ''
        self.Data.Output = ''
        for Url in Urls:
            Data = await GetSoupUrl(Url)
            Err = FilterKeyErr(Data)
            if (Err):
                self.Data.Output = 'Error loading %s, %s' % (Url, Err)
                break

            try:
                Scheme = TScheme(Script)
                Scheme.Debug = True
                Output = Scheme.Parse(Data.get('Soup')).GetData(['Err', 'Pipe', 'Warn'])
                self.Data.Output += json.dumps(Output, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder) + '\n'
                self.Data.Script = Script
            except Exception as E:
                self.Data.Output = 'Error %s' % (E)
            await asyncio.sleep(0.1)

    async def BtnSave(self):
        (Script, Err), Urls = self.CompileUrl()
        if (Err):
            self.Data.Output = 'Error compiler %s' % (Err)
            return

        Url = Urls[0]
        Data = await GetSoupUrl(Url)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.Output = 'Error loading %s, %s' % (Url, Err)
            return

        Scheme = TScheme(Script).Parse(Data.get('Soup'))
        Output = Scheme.GetData(['Err'])
        if (Output.get('Err')):
            self.Data.Output = 'Error pharser: %s' % Output.get('Err')
            return

        RequiredKey = ['name', 'price']
        Filtered = FilterKey(Scheme.GetPipe(), RequiredKey, dict)
        if (len(Filtered) < len(RequiredKey)):
            self.Data.Output = 'Error: Required keys %s' % (RequiredKey)
            return

        DataApi = await Api.DefHandler('set_scheme', {'scheme': Script, 'trust': self.Data.Admin})
        Err = FilterKeyErr(DataApi)
        if (Err):
            self.Data.Output = DataApi.get(Err)
        else:
            self.Data.Output = 'Saved'

    async def BtnInfo(self):
        Data = await GetSoupUrl(self.Data.Url0)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.Output = 'Error loading %s, %s, %s' % (self.Data.Url0, Err, Data.get('Msg'))
            return

        self.Data.Output = Data.get('Data')
        Arr = GetUrlInfo(Data)
        self.Data.Script = '\n'.join(Arr) + '\n'

    async def _Render(self):
        HasItems = await self.PostToForm()
        self.Data.Admin = (Session.Data.get('UserGroup') == 'admin')
        if (not HasItems):
             return

        if ('BtnMake' in self.Data):
            await self.BtnMake()
        elif ('BtnSave' in self.Data):
            await self.BtnSave()
        elif ('BtnInfo' in self.Data):
            await self.BtnInfo()
