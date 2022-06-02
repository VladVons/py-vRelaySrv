'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.11
License:     GNU, see LICENSE for more details
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
def GetNestedKey(aData: dict, aKeys: str, aDef = None) -> object:
    for Key in aKeys.split('.'):
        if (isinstance(aData, dict)):
            aData = aData.get(Key)
            if (aData is None):
                return aDef
        else:
            return aDef
    return aData


def FilterKey(aData: object, aKeys: list, aInstance: list) -> object:
    def _FilterKey(aData: object, aKeys: list, aRes: dict, aPath: str):
        if (type(aData) == dict):
            for Key, Val in aData.items():
                Path = (aPath + '.' + Key).lstrip('.')
                _FilterKey(Val, aKeys, aRes, Path)
                if (Key in aKeys):
                    if (aInstance == dict):
                        aRes[Path] = Val
                    elif (aInstance == list):
                        aRes.append(Val)
    if (aInstance == list) or (aInstance == dict):
        Res = aInstance()
        _FilterKey(aData, aKeys, Res, '')
        return Res
    else:
        raise ValueError('Must be dict or list')

def FilterKeyErr(aData: dict, aAsStr: bool = False) -> list:
    def _FilterKey(aData: object, aRes: list):
        if (type(aData) == dict):
            for Key, Val in aData.items():
                _FilterKey(Val, aRes)
                if (Key == 'Type') and (Val == 'Err'):
                    aRes.append(aData.get('Data'))
    Res = []
    _FilterKey(aData, Res)
    if (aAsStr):
        Res = ', '.join([str(x) for x in Res])
    return Res

def FilterNone(aData: dict, aTrue: bool) -> dict:
    return {
        Key: Val
        for Key, Val in aData.items()
        if ((Val is None) == aTrue)
    }


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

def GetMethodInfo(aObj) -> tuple:
    Name = aObj.__code__.co_name
    Args = aObj.__code__.co_varnames[:aObj.__code__.co_argcount]
    Repr = '%s(%s)' % (Name, ', '.join(Args))
    return (Name, Args, Repr)
