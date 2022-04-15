'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''


import json
import random

class TJsonEncoder(json.JSONEncoder):
    def default(self, aObj):
        Type = type(aObj).__name__
        if (Type == 'TDbList'):
            Res = aObj.DataExport()
        elif (Type == 'set'):
            Res = list(aObj)
        else:
            Res = str(aObj)
        return Res

    @staticmethod
    def Dumps(aObj):
        return json.dumps(aObj, cls=TJsonEncoder)


class TDictStr(dict):
    def __getattr__(self, aName: str) -> object:
        return self.get(aName, '')

def GetLeadCharCnt(aValue: str, aChar: str) -> int:
    return len(aValue) - len(aValue.lstrip(aChar))

def GetRandStr(aLen: int, aPattern = 'YourPattern') -> str:
    return ''.join((random.choice(aPattern)) for x in range(aLen))
