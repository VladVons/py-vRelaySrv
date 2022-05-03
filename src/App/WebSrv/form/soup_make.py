'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''

import json
import datetime
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TSoupScheme
from IncP.Log import Log
from IncP.Utils import TJsonEncoder, FormatJsonStr


_FieldPrefix = 'Script_'


class TForm(TFormBase):
    Title = 'Soup make'

    def StripDataLines(self, aPrefix: str):
        for Key, Val in self.Data.items():
            if (Key.startswith(aPrefix)) and (Val):
                Str = ''
                for Line in Val.splitlines():
                    Str += Line.strip() + '\n'
                self.Data[Key] = Str

    def Compile(self) -> tuple:
        Err = ''

        try:
            Path = json.loads('[%s]' % self.Data.Path)
        except ValueError as E:
            Path = []
            Err += '_Path: %s\n' % E.args

        Items = {}
        ItemsStr = []
        for Key, Val in self.Data.items():
            if (Key.startswith(_FieldPrefix)) and (Val) and (not Val.startswith('-')):
                Key = Key.replace(_FieldPrefix, '')
                try:
                    Items[Key] = json.loads(f'[{Val}]')
                except ValueError as E:
                    Err += '%s: %s\n' % (Key, E.args)

                ItemsStr.append('''
                            "%s": [
                                %s
                            ]''' % (Key, Val))
        Script = {
            'Product': {
                '-Info': {
                    'Url': self.Data.Url,
                    'Date': datetime.date.today().strftime('%Y-%m-%d')
                },
                '_Group1': {
                    '_Path': [Path],
                    '_Items': Items
                }
            }
        }

        ScriptStr = '''
            {
                "Product": {
                    "-Info": {
                        "Url": "%s",
                        "Date": "%s"
                    },
                    "_Group1": {
                        "_Path": [[%s]],
                        "_Items": {
                            %s
                        }
                    }
                }
            }
        ''' % (self.Data.Url, datetime.date.today().strftime('%Y-%m-%d'), self.Data.Path, ','.join(ItemsStr))

        return (Script, FormatJsonStr(ScriptStr), Err)

    async def Render(self):
        if (await self.PostToForm()):
            self.StripDataLines(_FieldPrefix)
            Script, ScriptStr, Err = self.Compile()
            if (Err):
                self.Data.Script = ''
                self.Data.Output = Err
            else:
                Download = TDownload()
                UrlDown = await Download.Get(self.Data.Url)
                if (UrlDown.get('Err')):
                    self.Data.Output = 'Error loading %s, %s' % (self.Data.Url, UrlDown.get('Msg'))
                else:
                    Data = UrlDown['Data']
                    Status = UrlDown['Status']
                    if (Status == 200):
                        self.Data.Script = ScriptStr
                        Soup = BeautifulSoup(Data, 'lxml')
                        Scheme = TSoupScheme.ParseKeys(Soup, Script)
                        self.Data.Output = json.dumps(Scheme, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
                    else:
                        self.Data.Output = 'Error loading %s' % (self.Data.Url)
        return self._Render()
