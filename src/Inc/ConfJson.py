'''

'''


import json
from Inc.Util.UObj import GetNestedKey, DictJoin


class TConfJson(dict):
    @staticmethod
    def Join(aDicts: list) -> dict:
        Res = {}
        for x in aDicts:
            if (x):
                Data = DictJoin(Res, x)
                Res.update(Data)
        return Res

    def JoinKeys(self, aKey: list) -> dict:
        Data = [GetNestedKey(self, x, {}) for x in aKey]
        return self.Join(Data)

    def Load(self, aFile: str):
        with open(aFile, 'r') as File:
            Data = json.load(File)
            self.Init(Data)

    def Init(self, aData: dict):
        super().__init__(aData)
