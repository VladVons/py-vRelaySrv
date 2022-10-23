# Created: 2022.10.06
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import sys
import time
#
from Inc.ConfJson import TConfJson
from Inc.Util.Mod import DynImport
from IncP.Log import Log


class TPluginApp():
    def __init__(self):
        self.Data = {}
        self.Conf = {}
        self.Path = 'Task.Plugin'

    def Init(self, aPlugin: str):
        Dir, ModName = aPlugin.split('.')

        self.Conf = TConfJson()
        self.Conf.LoadList([f'Conf/{Dir}~{ModName}.json', f'{Dir}/{ModName}.json'])
        Conf = self.Conf.get('Conf', [])
        self.Conf.LoadList(Conf)
        self.Path = f'{aPlugin}.Plugin'

    @staticmethod
    def _Filter(aData: list[str]) -> list:
        return [x for x in aData if (not x.startswith('-'))]

    async def Load(self, aName: str, aDepth: int) -> dict:
        if (self.Data.get(aName) is None):
            Tab = '-' * (aDepth + 1)
            Log.Print(1, 'i', '%sLoad app %s' % (Tab, aName))

            Depends = self.Conf.GetKey('Plugin.' + aName + '.Depends', [])
            Depends = self._Filter(Depends)
            for Depend in Depends:
                if (self.Data.get(Depend) is None):
                    Log.Print(1, 'i', '%s%s depends on %s' % (Tab, aName, Depend))
                await self.Load(Depend, aDepth + 1)

            TClass = DynImport(self.Path + '.' + aName, 'T' + aName)
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
        TimeStart = time.time()
        Log.Print(1, 'i', 'Start. TPluginApp.Run()')
        for Plugin in self._Filter(self.Conf.get('Plugins', [])):
            await self.Load(Plugin, 0)
        Log.Print(1, 'i', 'Finish. TPluginApp.Run(). Time: %0.2f' % (time.time() - TimeStart))
