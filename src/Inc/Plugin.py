'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.01.30
License:     GNU, see LICENSE for more details
'''


try:
  import asyncio
except:
  import uasyncio as asyncio

import gc
import os
import sys
#
from Inc.Conf import TConf
from Inc.ConfClass import TConfClass
from IncP.Log import Log


class TPlugin(dict):
    def Find(self, aKey: str) -> list:
        return [Val[0] for Key, Val in self.items() if aKey in Key]

    def AddTask(self, aModule, aPath: str):
        gc.collect()
        Log.Print(1, 'i', 'Plugin %s' % (aPath))

        File = 'Conf/' + aPath.replace('.', '~')
        Conf = TConf(File + '.py')
        Conf.Load()
        ConfClass = TConfClass(File + '.json', Conf)
        ConfClass.Load()

        Arr = aModule.Main(Conf)
        if (Arr):
            Class, AFunc= Arr
            self[aPath] = (Class, asyncio.create_task(AFunc))
            if (Conf) or (ConfClass):
                Class.CC = ConfClass

    def LoadDir(self, aDir: str):
        Files = os.ilistdir(aDir)
        for Info in Files:
            if (Info[1] & 0x4000): # is dir
                DirName = Info[0]
                self.LoadMod(aDir.replace('/', '.') + '.' + DirName)

    def LoadList(self, aModules: str, aSkip: str = ''):
        Skip = aSkip.split()
        for Module in aModules.split():
            if (not Module in Skip):
                self.LoadMod(Module)

    def LoadMod(self, aPath: str):
        if (aPath == '') or (aPath.startswith('-')) or (self.get(aPath)):
            return

        __import__(aPath)
        Mod = sys.modules.get(aPath)
        Enable = getattr(Mod, 'Enable', True)
        if (Enable):
            Depends = getattr(Mod, 'Depends', '')
            for x in Depends.split():
                if (x):
                    Log.Print(1, 'i', '%s depends on %s' % (aPath, x))
                    self.LoadMod(x)
            self.AddTask(Mod, aPath)
        else:
            Log.Print(1, 'i', '%s disabled' % (aPath))

    async def _Post(self, aTasks, aOwner, aMsg, aFunc) -> dict:
        R = {}
        for Key, (Class, Task) in aTasks:
            if (Class != aOwner) and (hasattr(Class, aFunc)):
                Func = getattr(Class, aFunc)
                R[Key] = await Func(aOwner, aMsg)
                if (R[Key] == aOwner):
                    break
        return R

    async def Post(self, aOwner, aMsg, aFunc: str = '_DoPost'):
        return await self._Post(self.items(), aOwner, aMsg, aFunc)

    def PostNonAsync(self, aOwner, aMsg, aFunc: str = '_DoPost'):
        return asyncio.create_task(self.Post(aOwner, aMsg, aFunc))

    async def Stop(self, aPath: str) -> bool:
        Obj = self.get(aPath)
        if (Obj):
            await self._Post([(aPath, Obj)], None, None, '_DoStop')
            await asyncio.sleep(0.5)
            Obj[1].cancel()
            del self[aPath]
            return True

    async def StopAll(self):
        for Key in list(self.keys()):
            await self.Stop(Key)

    async def Run(self):
        Tasks = [v[1] for v in self.values()]
        await asyncio.gather(* Tasks)


Plugin = TPlugin()
