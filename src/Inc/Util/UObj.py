'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2020.02.21
License:     GNU, see LICENSE for more details
'''


def GetTree(aObj, aPrefix: str = '', aDepth: int = 99) -> list:
    Res = []
    if (aDepth > 0):
        Type = type(aObj).__name__
        if (Type == 'dict'):
            for Key in aObj:
                Data = GetTree(aObj[Key], aPrefix + '/' + Key, aDepth - 1)
                Res.extend(Data)
        elif (Type == 'list'):
            for Obj in aObj:
                Data = GetTree(Obj, aPrefix, aDepth - 1)
                Res.extend(Data)
        else:
            Data = {'Key': aPrefix, 'Val': aObj}
            Res.append(Data)
    return Res

def GetClassPath(aClass):
    def GetClassPathRecurs(aInstance: object, aPath: str = '', aDepth: int = 99) -> str:
        Instance = aInstance.__bases__
        if ( (Instance) and (aDepth > 0) ):
            aPath = GetClassPathRecurs(Instance[0], aPath, aDepth - 1)
        return aPath + '/' + aInstance.__name__

    return GetClassPathRecurs(aClass.__class__)

def DictUpdate(aMaster: dict, aSlave: dict, aJoin = False, aDepth: int = 99) -> object:
    '''
    DictJoin({3: [1, 2, 3]}, {3: [4]})
    '''
    Type = type(aSlave)
    if (aDepth > 0):
        if (Type == dict):
            Res = aMaster
            for Key, Val in aSlave.items():
                Tmp = aMaster.get(Key)
                if (Tmp is None):
                    Tmp = {} if isinstance(Val, dict) else []
                Data = DictUpdate(Tmp, Val, aJoin, aDepth - 1)
                Res[Key] = Data
        elif (Type == list):
            Res = aMaster
            for Val in aSlave:
                Data = DictUpdate(None, Val, aJoin, aDepth - 1)
                if (aJoin):
                    Res.append(Data)
                else:
                    Res = Data
        else:
            Res = aSlave
        return Res

def GetNestedKey(aData: dict, aKeys: str, aDef = None) -> object:
    for Key in aKeys.split('.'):
        if (isinstance(aData, dict)):
            aData = aData.get(Key)
            if (aData is None):
                return aDef
        else:
            return aDef
    return aData

def GetNotNone(aData: dict, aKey: str, aDef: object) -> object:
    Res = aData.get(aKey, aDef)
    if (Res is None):
        Res = aDef
    return Res
