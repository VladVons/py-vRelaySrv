# Created: 2022.04.11
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import asyncio
import datetime
import json
#
from Inc.Misc.Misc import TJsonEncoder, FormatJsonStr, FilterKey, FilterKeyErr
from Inc.Scheme.Scheme import TScheme
from IncP.Download import GetSoupUrl
from .FormBase import TFormBase
from ..Api import Api
from ..Session import Session
from ..Utils import GetUrlInfo, GetApiHelp


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
            json.loads('[%s]' % self.Data.pipe)
            json.loads('{%s}' % self.Data.var)
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
                "product": {
                    "info": {
                        "author": "%s",
                        "date": "%s",
                        "url": [
                            %s
                        ],
                        "comment": "%s"
                    },
                    "var": {
                        %s
                    },
                    "pipe": [
                        %s,
                        ["as_dict", {
                            %s
                        }]
                    ]
                }
            }
        ''' % (
                Session.Data.get('user_name'),
                datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                Urls,
                self.Data.comment,
                self.Data.var,
                self.Data.pipe,
                ','.join(Items)
            )

        return (FormatJsonStr(ScriptStr), '\n'.join(Err))

    def CompileUrl(self):
        Urls = [
            Val
            for Key, Val in self.Data.items()
            if (Val and Key.startswith('url'))
        ]

        FieldsScript = [Key for Key in self.Data if Key.startswith(_FieldPrefix)] + ['pipe']
        self.StripDataLines(FieldsScript)
        return (self.Compile(Urls), Urls)

    async def BtnMake(self):
        if (self.Data.admin):
            if (self.Data.get('btn_moderate_flag') == 'true'):
                #ScriptOrig = json.loads(self.Data.script)
                pass
        else:
            if (self.Data.get('btn_save_flag') == 'disabled'):
                self.Data.btn_save_disabled = 'disabled'

        (Script, Err), Urls = self.CompileUrl()
        if (Err):
            self.Data.output = Err
            return

        self.Data.script = ''
        self.Data.output = ''
        for Url in Urls:
            Data = await GetSoupUrl(Url)
            Err = FilterKeyErr(Data)
            if (Err):
                self.Data.output = 'Error loading %s, %s' % (Url, Err)
                break

            try:
                Scheme = TScheme(Script)
                Scheme.Debug = True
                Output = Scheme.Parse(Data.get('soup')).GetData(['err', 'pipe', 'warn'])
                Unknown = [x for x in Output.get('err', []) if 'unknown' in x]
                if (Unknown):
                    Output['help'] = GetApiHelp()

                self.Data.output += json.dumps(Output, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder) + '\n'
                self.Data.script = Script
            except Exception as E:
                self.Data.output = 'Error %s' % (E)
            await asyncio.sleep(0.1)

    async def BtnSave(self):
        (Script, Err), Urls = self.CompileUrl()
        if (Err):
            self.Data.output = 'Error compiler %s' % (Err)
            return

        Url = Urls[0]
        Data = await GetSoupUrl(Url)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.output = 'Error loading %s, %s' % (Url, Err)
            return

        Scheme = TScheme(Script).Parse(Data.get('soup'))
        Output = Scheme.GetData(['err'])
        if (Output.get('err')):
            self.Data.output = 'Error pharser: %s' % Output.get('err')
            return

        RequiredKey = ['name', 'price']
        Filtered = FilterKey(Scheme.GetPipe(), RequiredKey, dict)
        if (len(Filtered) < len(RequiredKey)):
            self.Data.output = 'Error: Required keys %s' % (RequiredKey)
            return

        DataApi = await Api.DefHandler('set_scheme', {'scheme': Script, 'trust': self.Data.admin})
        Err = FilterKeyErr(DataApi)
        if (Err):
            self.Data.output = DataApi.get(Err)
        else:
            self.Data.output = 'saved'

    async def BtnInfo(self):
        Data = await GetSoupUrl(self.Data.url0)
        Err = FilterKeyErr(Data)
        if (Err):
            self.Data.output = 'Error loading %s, %s, %s' % (self.Data.url0, Err, Data.get('msg'))
            return

        self.Data.output = Data.get('data')
        Arr = GetUrlInfo(Data)
        self.Data.script = '\n'.join(Arr) + '\n'

    async def _Render(self):
        HasItems = await self.PostToForm()
        self.Data.admin = (Session.Data.get('user_group') == 'admin')
        if (not HasItems):
            return

        if ('btn_make' in self.Data):
            await self.BtnMake()
        elif ('btn_save' in self.Data):
            await self.BtnSave()
        elif ('btn_info' in self.Data):
            await self.BtnInfo()
