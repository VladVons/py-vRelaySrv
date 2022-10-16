'''
VladVons@gmail.com
2022.10.06
'''


import sys
import time
#
from Inc.ConfJson import TConfJson
from Inc.Util.UMod import DynImport
from IncP.Log import Log


class TPluginApp():
    def __init__(self, aConf: TConfJson):
        self.Conf = aConf
        self.Data = {}

    @staticmethod
    def _Filter(aData: list[str]) -> list:
        return [x for x in aData if (not x.startswith('-'))]

    async def Load(self, aName: str, aDepth: int) -> dict:
        if (self.Data.get(aName) is None):
            Tab = '-' * (aDepth + 1)
            Log.Print(1, 'i', '%sLoad %s' % (Tab, aName))

            Depends = self.Conf.GetKey('Plugin.' + aName + '.Depends', [])
            Depends = self._Filter(Depends)
            for Depend in Depends:
                if (self.Data.get(Depend) is None):
                    Log.Print(1, 'i', '%s%s depends on %s' % (Tab, aName, Depend))
                await self.Load(Depend, aDepth + 1)

            TClass = DynImport('IncP.Plugin.' + aName, 'T' + aName)
            if (TClass):
                TimeStart = time.time()
                Class = TClass()
                Class.Parent = self
                Class.Depends = Depends
                Class.Name = aName
                Class.Depth = aDepth
                Class.Conf = TConfJson(self.Conf.JoinKeys(['Common', 'Plugin.' + aName]))
                self.Data[aName] = await Class.Run()
                Log.Print(1, 'i', '%sFinish %s. Time: %0.2f' % (Tab, aName, time.time() - TimeStart))
            else:
                Log.Print(1, 'e', '%sErr loading %s' % (Tab, aName))
                sys.exit(1)

    async def Run(self):
        for Plugin in self._Filter(self.Conf.get('Plugins', [])):
            await self.Load(Plugin, 0)
