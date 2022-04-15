'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''

import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme, FormatJsonStr
from IncP.Log import Log
from IncP.Utils import TJsonEncoder


_FieldPrefix = 'Script_'


class TForm(TFormBase):
    Title = "Soup make"

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
        ItemsStr = ''
        for Key, Val in self.Data.items():
            if (Key.startswith(_FieldPrefix)) and (Val):
                Key = Key.replace(_FieldPrefix, '')
                try:
                    Items[Key] = json.loads(f'[{Val}]')
                except ValueError as E:
                    Err += '%s: %s\n' % (Key, E.args)
                ItemsStr += '''
                            "%s": [
                                %s
                            ]''' % (Key, Val)
        Script = {
            'Product': {
                '_Group1': {
                    '_Path': [Path],
                    '_Items': Items
                }
            }
        }

        ScriptStr = '''
            {
                "Product": {
                    "_Group1": {
                        "_Path": [%s],
                        "_Items": {
                            %s
                        }
                    }
                }
            }

        ''' % (self.Data.Path, ItemsStr)

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
                        Scheme = TScheme.ParseKeys(Soup, Script)
                        self.Data.Output = json.dumps(Scheme, indent=2, sort_keys=True, ensure_ascii=False, cls=TJsonEncoder)
                    else:
                        self.Data.Output = 'Error loading %s' % (self.Data.Url)
        return self._Render()
