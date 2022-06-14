'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
'''

import asyncio
import datetime
import json
#
from ..Api import Api
from .FForm import TFormBase
from IncP.Download import GetUrlSoup
from IncP.Log import Log
from IncP.Scheme import TScheme
from IncP.Utils import TJsonEncoder, FormatJsonStr, FilterKey, FilterKeyErr, GetNestedKey


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
                        ]
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
                self.Session['UserName'],
                datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                Urls,
                self.Data.Var,
                self.Data.Pipe, ','.join(Items)
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
        (Script, Err), Urls = self.CompileUrl()
        if (Err):
            self.Data.Output = Err
            return

        if (not self.Data.Admin) and (self.Data.get('BtnSaveFlag') == 'disabled'):
            self.Data.BtnSaveDisabled = 'disabled'

        self.Data.Script = ''
        self.Data.Output = ''
        for Url in Urls:
            Soup = await GetUrlSoup(Url)
            if (Soup):
                Scheme = TScheme(Script)
                Scheme.Debug = True
                Output = Scheme.Parse(Soup).GetData(['Err', 'Pipe', 'Warn'])
                self.Data.Output += json.dumps(Output, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder) + '\n'
                self.Data.Script = Script
            else:
                self.Data.Output = 'Error loading %s' % (Url)
                break
            await asyncio.sleep(0.1)

    async def BtnSave(self):
        (Script, Err), Urls = self.CompileUrl()
        if (Err):
            self.Data.Output = 'Error compiler %s' % (Err)
            return

        Soup = await GetUrlSoup(Urls[0])
        if (not Soup):
            self.Data.Output = 'Error loading %s' % (Urls[0])
            return

        Scheme = TScheme(Script).Parse(Soup)
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

    async def _Render(self):
        HasItems = await self.PostToForm()
        self.Data.Admin = (self.Session.get('UserGroup') == 'admin')
        if (not HasItems):
             return

        if ('BtnMake' in self.Data):
            await self.BtnMake()
        elif ('BtnSave' in self.Data):
            await self.BtnSave()
