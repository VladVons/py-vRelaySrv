'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''


import json
import random


#--- Json ---
class TJsonEncoder(json.JSONEncoder):
    def default(self, aObj):
        Type = type(aObj).__name__
        if (Type == 'TDbList'):
            Res = aObj.Export()
        elif (Type == 'set'):
            Res = list(aObj)
        else:
            Res = str(aObj)
        return Res

    @staticmethod
    def Dumps(aObj):
        return json.dumps(aObj, cls=TJsonEncoder)

def FormatJsonStr(aScript: str, aPad: int = 2, aChar: str = ' ') -> str:
    Res = []
    Level = 0
    Lines = aScript.splitlines()
    for Line in Lines:
        Line = Line.strip()
        if (Line):
            if (Line[-1] in ['{', '[']):
                Spaces = Level * aPad
                Level += 1
            elif (Line[0] in ['}', ']']):
                Level -= 1
                Spaces = Level * aPad
            else:
                Spaces = Level * aPad
            Res.append((aChar * Spaces) + Line)
    return '\n'.join(Res)


#--- Dictionary ---
class TDictStr(dict):
    def __getattr__(self, aName: str) -> object:
        return self.get(aName, '')

def GetNestedKey(aData: dict, aKeys: str, aDef = None) -> object:
    for Key in aKeys.split('.'):
        if (isinstance(aData, dict)):
            aData = aData.get(Key)
            if (aData is None):
                return aDef
        else:
            return aDef
    return aData


#--- String ---
def GetLeadCharCnt(aValue: str, aChar: str) -> int:
    return len(aValue) - len(aValue.lstrip(aChar))

def GetRandStr(aLen: int) -> str:
    def Range(aStart: int, aEnd: int) -> list:
        return [chr(i) for i in range(aStart,  aEnd)]

    Pattern = Range(48, 57) + Range(65, 90) + Range(97, 122)
    Rand = random.sample(Pattern, aLen)
    return ''.join(Rand)

def GetRandStrPattern(aLen: int, aPattern = 'YourPattern') -> str:
    return ''.join((random.choice(aPattern)) for x in range(aLen))

