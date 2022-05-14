'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''

import json
import datetime
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

    def Compile(self) -> tuple:
        Err = ''

        try:
            Path = json.loads('[%s]' % self.Data.Path)
        except ValueError as E:
            Path = []
            Err += '_Path: %s\n' % E.args

        ItemsStr = []
        for Key, Val in self.Data.items():
            if (Key.startswith(_FieldPrefix)) and (Val) and (not Val.startswith('-')):
                Key = Key.replace(_FieldPrefix, '')
                try:
                    json.loads(f'[{Val}]')
                except ValueError as E:
                    Err += '%s: %s\n' % (Key, E.args)

                ItemsStr.append('''
                            "%s": [
                                %s
                            ]''' % (Key, Val))
        ScriptStr = '''
            {
                "Product": {
                    "Info": {
                        "Url": "%s",
                        "Date": "%s"
                    },
                    "Pipe": [
                        %s,
                        ["as_dict", {
                            %s
                        }]
                    ]
                }
            }
        ''' % (self.Data.Url, datetime.date.today().strftime('%Y-%m-%d'), self.Data.Path, ','.join(ItemsStr))

        return (FormatJsonStr(ScriptStr), Err)

    async def Render(self):
        if (await self.PostToForm()):
            FieldsScript = [Key for Key in self.Data if Key.startswith(_FieldPrefix)] + ['Path']
            self.StripDataLines(FieldsScript)

            Script, Err = self.Compile()
            if (Err):
                self.Data.Script = ''
                self.Data.Output = Err
            else:
                Soup = await GetUrlSoup(self.Data.Url)
                if (Soup):
                    Output = TScheme(Script).Parse(Soup).GetData(['Err', 'Pipe'])
                    self.Data.Output = json.dumps(Output, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
                    self.Data.Script = Script
                else:
                    self.Data.Output = 'Error loading %s' % (self.Data.Url)
        return self._Render()
