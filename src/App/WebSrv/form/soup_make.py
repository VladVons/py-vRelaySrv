import json
from bs4 import BeautifulSoup
#
from .FForm import TFormBase
from IncP.Download import TDownload
from IncP.Scheme import TScheme
from IncP.Log import Log


def GetLeadCharCnt(aValue: str, aChar: str) -> int:
    return len(aValue) - len(aValue.lstrip(aChar))

def FormatScript(aScript: str) -> str: 
    Res = []
    Lines = aScript.splitlines()
    PadSpaces = GetLeadCharCnt(Lines[1], ' ')
    for Idx, Line in enumerate(Lines):
        if (Line.strip()):
            if (Line.startswith(' ')):
                Line = Line[PadSpaces:]
            else:
                Spaces = GetLeadCharCnt(Res[-1], ' ')
                Line = (' ' * Spaces) + Line
            Res.append(Line)
    return '\n'.join(Res)

class TForm(TFormBase):
    Title = "Soup make"
    _Prefix = 'Script_'

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
            if (Key.startswith(self._Prefix)) and (Val):
                Key = Key.replace(self._Prefix, '')
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

        return (Script, FormatScript(ScriptStr), Err)
    
    async def Render(self):
        if (await self.PostToForm()):
            self.StripDataLines('Script_')
            Script, ScriptStr, Err = self.Compile()
            if (Err):
                self.Data.Script = ''
                self.Data.Output = ''
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
                        self.Data.Output = json.dumps(Scheme,  indent=2, sort_keys=True, ensure_ascii=False)
                    else:
                        self.Data.Output = 'Error loading %s' % (self.Data.Url) 
        return self._Render()
