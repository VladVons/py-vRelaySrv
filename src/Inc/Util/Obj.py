# Created: 2020.02.21
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


def GetTree(aObj, aMaxDepth: int = 99):
    def GetTreeRecurs(aObj, aPrefix: str, aDepth: int):
        if (aDepth < aMaxDepth):
            Type = type(aObj)
            if (Type == dict):
                yield [True, aPrefix, aObj, aDepth]
                for Key in aObj:
                    yield from GetTreeRecurs(aObj[Key], aPrefix + '/' + Key, aDepth + 1)
            elif (Type in [list, tuple, set]):
                yield [True, aPrefix, aObj, aDepth]
                for Obj in aObj:
                    yield from GetTreeRecurs(Obj, aPrefix, aDepth + 1)
            elif (Type in [str, int, float, bool]):
                yield [False, aPrefix, aObj, aDepth]
            elif (Type.__name__ in ['method']):
                yield [False, aPrefix + '()', aObj, aDepth]
            else:
                ClassName = aPrefix + '/' + aObj.__class__.__name__
                yield [True, ClassName, aObj, aDepth]
                for Key in dir(aObj):
                    if (not Key.startswith('_')):
                        Obj = getattr(aObj, Key)
                        yield from GetTreeRecurs(Obj, ClassName + '/' + Key, aDepth + 1)
    yield from GetTreeRecurs(aObj, '', 0)

def GetClassPath(aClass):
    def GetClassPathRecurs(aInstance: object, aPath: str = '', aDepth: int = 99) -> str:
        Instance = aInstance.__bases__
        if ( (Instance) and (aDepth > 0) ):
            aPath = GetClassPathRecurs(Instance[0], aPath, aDepth - 1)
        return aPath + '/' + aInstance.__name__

    return GetClassPathRecurs(aClass.__class__)

def DictUpdate(aMaster: dict, aSlave: dict, aJoin = False, aDepth: int = 99) -> object:
    '''
    DictJoin({3: [1, 2, 3]}, {3: [4]}) -> {3: [1, 2, 3, 4]}
    '''

    if (aDepth <= 0):
        return

    Type = type(aSlave)
    if (Type == dict):
        if (aMaster is None):
            aMaster = {}
        Res = aMaster

        for Key, Val in aSlave.items():
            Tmp = aMaster.get(Key)
            if (Tmp is None):
                Tmp = {} if isinstance(Val, dict) else []
            Data = DictUpdate(Tmp, Val, aJoin, aDepth - 1)
            Res[Key] = Data
    elif (Type == list):
        Res = [] if (aMaster is None ) else aMaster
        for Val in aSlave:
            Data = DictUpdate(None, Val, aJoin, aDepth - 1)
            if (aJoin):
                Res.append(Data)
            else:
                Res = Data
    else:
        Res = aSlave
    return Res

def DeepGet(aData: dict, aDotKeys: str, aDef = None) -> object:
    # more complex https://jmespath.org/examples.html
    for Key in aDotKeys.split('.'):
        if (isinstance(aData, dict)) or (hasattr(aData, 'get')):
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

def Filter(aData: dict, aKeys: list) -> dict:
    return {Key: aData[Key] for Key in aKeys }
