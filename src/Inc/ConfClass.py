'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.01.03
License:     GNU, see LICENSE for more details
'''


import os
import json
#
from IncP.Log import Log
from Inc.Conf import TConf, TDictDef


class TConfClass(TConf):
    def __init__(self, aFile: str, aConf: TDictDef = None):
        super().__init__(aFile)

        if (aConf is None):
            aConf = TDictDef()
        self.Conf = aConf

    def _Replace(self, aData: str) -> str:
        Delim = '%'
        #Items = re.findall(Macro + '(.*?)' + Macro, aData)
        Items = aData.split(Delim)[1::2]
        for Item in Items:
            Repl = self.Conf.get(Item)
            if (Repl is None):
                Log.Print(1, 'e', 'unknown ' + Item)
            else:
                Find = Delim + Item + Delim
                if (not isinstance(Repl), str):
                    Repl = str(Repl).replace("'", '"')
                aData = aData.replace(Find, Repl)
        return aData

    def _Load(self, aFile: str):
        with open(aFile) as hF:
            Data = self._Replace(hF.read())
            try:
                Data = json.loads(Data)
                for Item in Data.get('Classes', []):
                    Alias = Item.get('Alias')
                    Class = Item.get('Class')
                    Param = Item.get('Param', {})
                    Module = Item.get('Module')

                    Mod = __import__(Module, None, None, [Class])
                    TClass = getattr(Mod, Class)
                    Obj = TClass(** Param)
                    Obj.Descr = Item.get('Descr', '')
                    Obj.Alias = Alias

                    self[Alias] = Obj
            except Exception as E:
                Log.Print(1, 'x', '_Load()', aE = E)
                print('Data-x', Data)

    '''
     def _DirList(self, aDir):
        return [aDir + '/' + File for File in sorted(os.listdir(aDir)) if File.endswith('.json')]

    def Loads(self, aFiles: list, aVars: dict = {}):
        for File in aFiles:
            self.Load(File)

    def LoadDir(self, aDir: str, aVars: dict = {}):
        self.Loads(self._DirList(aDir), aVars)

    def LoadPlugin(self, aDir: str, aPlugin: list, aVars: dict = {}):
        DirList = self._DirList(aDir)
        Files = [DL for DL in DirList if any(P in DL for P in aPlugin)]
        self.Loads(Files, aVars)

    def Clear(self):
         for Item in list(self.keys()):
            del self[Item]
'''
