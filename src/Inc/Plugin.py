# Created: 2023.01.20
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import sys
#
from IncP.Log import Log


class TPlugin(dict):
    def __init__(self, aDir: str = ''):
        super().__init__()
        self.Dir = aDir

    def _Create(self, aModule: object, aPath: str) -> object:
        raise NotImplementedError()

    def Find(self, aKey: str) -> list:
        return [Val[0] for Key, Val in self.items() if aKey in Key]

    def LoadMod(self, aPath: str, aRegister: bool = True) -> dict:
        Res = {}
        if (not aPath) or (aPath.startswith('-')) or (self.get(aPath)):
            return Res

        Path = self.Dir.replace('/', '.') + '.' + aPath
        __import__(Path)
        Mod = sys.modules.get(Path)
        Enable = getattr(Mod, 'Enable', True)
        if (Enable):
            Depends = getattr(Mod, 'Depends', '')
            for x in Depends.split():
                if (x):
                    Log.Print(1, 'i', '%s depends on %s' % (aPath, x))
                    ResF = self.LoadMod(x)
                    Res.update(ResF)
            Obj = self._Create(Mod, aPath)
            if (Obj):
                if (aRegister):
                    self[aPath] = Obj
                Res[aPath] = Obj
        else:
            Log.Print(1, 'i', '%s disabled' % (aPath))
        return Res

    def LoadList(self, aPath: str, aSkip: str = ''):
        Skip = aSkip.split()
        for Path in aPath.split():
            if (not Path in Skip):
                self.LoadMod(Path)

    def LoadDir(self, aDir: str):
        Files = os.listdir(aDir)
        for Info in Files:
            if (Info[1] & 0x4000): # is dir
                DirName = Info[0]
                self.LoadMod(aDir.replace('/', '.') + '.' + DirName)
