'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''

import json
import datetime
import asyncio
#
from IncP.Log import Log
from IncP.Scheme import TScheme
from IncP.Utils import TJsonEncoder, FormatJsonStr
from IncP.Download import GetUrlSoup
from .FForm import TFormBase


_FieldPrefix = 'Script_'


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
        except ValueError as E:
            Err.append('Pipe: %s\n' % E.args)

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
                        "Date": "%s",
                        "Url": [
                            %s
                        ]
                    },
                    "Pipe": [
                        %s,
                        ["as_dict", {
                            %s
                        }]
                    ]
                }
            }
        ''' % (datetime.date.today().strftime('%Y-%m-%d'), Urls, self.Data.Pipe, ','.join(Items))

        return (FormatJsonStr(ScriptStr), '\n'.join(Err))

    async def _Render(self):
        if (await self.PostToForm()):
            Urls = [
                Val
                for Key, Val in self.Data.items()
                if (Val and Key.startswith('Url'))
            ]

            FieldsScript = [Key for Key in self.Data if Key.startswith(_FieldPrefix)] + ['Pipe']
            self.StripDataLines(FieldsScript)

            self.Data.Script = ''
            Script, Err = self.Compile(Urls)
            if (Err):
                self.Data.Output = Err
            else:
                self.Data.Output = ''

                for Url in Urls:
                    Soup = await GetUrlSoup(Url)
                    if (Soup):
                        Output = TScheme(Script).Parse(Soup).GetData(['Err', 'Pipe'])
                        self.Data.Output += json.dumps(Output, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder) + '\n'
                        self.Data.Script = Script
                    else:
                        self.Data.Output = 'Error loading %s' % (Url)
                        break
                    await asyncio.sleep(0.1)
