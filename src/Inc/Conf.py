'''
Author:      Vladimir Vons, Oster Inc.
Created:     2018.06.10
License:     GNU, see LICENSE for more details
Description:

abrevation for RAM saving
R - Result
K - Key
V - Value
'''


import os, sys
#
from .Util.UFS import FileExists
from .Log  import Log


def ImportMod(aFile: str, aMod: list = ['*']):
    #aMod = ['Main']

    #__import__(aPath)
    #Mod = sys.modules.get(aPath)
    return __import__(aFile.replace('/', '.'), None, None, aMod)


class TConfD(dict):
    def __init__(self, aFile: str):
        super().__init__()

        self.File = aFile
        self.Def = None

    def __getattr__(self, aName: str):
        return self.Get(aName)

    def Load(self):
        Name, Ext = self.File.split('.')
        for Item in [Name, Name + '_' + sys.platform]:
            File = Item + '.' + Ext
            if (FileExists(File)):
                self._Load(File)

    def Get(self, aName: str):
        Res = self.get(aName)
        if (Res is None) and (self.Def):
            Res = self.Def.Get(aName)
        return Res

class TConf(TConfD):
    def _Load(self, aFile: str):
        Name, _ = aFile.split('.')
        Obj = ImportMod(Name)
        Keys = [O for O in dir(Obj) if (not O.startswith('__'))]
        for Key in Keys:
            self[Key] = getattr(Obj, Key, None)

    def Save(self):
        with open(self.File, 'w') as File:
            for K, V in sorted(self.items()):
                if (type(V) is str):
                    V = "'" + V + "'"
                File.write('%s = %s\n' % (K, V))
