# Created: 2018.06.10
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import sys
#
from .Util.FS import FileExists


def ImportMod(aFile: str, aMod: list = None):
    if (aMod is None):
        aMod = ['*']

    #aMod = ['Main']
    #__import__(aPath)
    #Mod = sys.modules.get(aPath)
    return __import__(aFile.replace('/', '.'), None, None, aMod)


class TDictDef(dict):
    def __init__(self, aDef: object = None, aData: dict = None):
        self.Def = aDef

        if (aData is None):
            aData = {}
        self.SetData(aData)

    def __getattr__(self, aName: str) -> object:
        return self.get(aName, self.Def)

    def Get(self, aName: str) -> object:
        if (isinstance(self.Def, dict)):
            return self.get(aName, self.Def.get(aName))

    def SetData(self, aData: dict):
        super().__init__(aData)


class TConf(TDictDef):
    def __init__(self, aFile: str):
        super().__init__()
        self.File = aFile

    def Load(self):
        Name, Ext = self.File.split('.')
        for Item in [Name, Name + '_' + sys.platform]:
            File = Item + '.' + Ext
            if (FileExists(File)):
                    self._Load(File)

    def _Load(self, aFile: str):
        Name, *_ = aFile.split('.')
        Obj = ImportMod(Name)
        Keys = [x for x in dir(Obj) if (not x.startswith('__'))]
        for Key in Keys:
            self[Key] = getattr(Obj, Key, None)

    def Save(self):
        with open(self.File, 'w', encoding = 'utf-8') as File:
            for K, V in sorted(self.items()):
                if (isinstance(V, str)):
                    V = "'" + V + "'"
                File.write('%s = %s\n' % (K, V))
