'''
VladVons@gmail.com
2022.10.04
'''

import os
import json
from Inc.Util.UObj import GetNestedKey, DictUpdate
from Inc.UtilP.UFS import GetFiles


class TConfJson(dict):
    def Init(self, aData: dict):
        super().__init__(aData)

    def _ReadFile(self, aFile: str) -> dict:
        with open(aFile, 'r', encoding = 'utf-8') as File:
            return json.load(File)

    @staticmethod
    def _Join(aDict: list) -> dict:
        Res = {}
        for x in aDict:
            if (x):
                Data = DictUpdate(Res, x, True)
                Res.update(Data)
        return Res

    def JoinKeys(self, aKey: list) -> dict:
        Data = [GetNestedKey(self, x, {}) for x in aKey]
        return self._Join(Data)

    def LoadDir(self, aDir: str):
        Files = GetFiles(aDir, '.json')
        for File in Files:
            self.LoadFile(File, True)

    def LoadFile(self, aFile: str, aJoin: bool = False):
        Data = self._ReadFile(aFile)
        if (aJoin):
            Data = self._Join([self, Data])
            self.Init(Data)
        else:
            self.update(Data)