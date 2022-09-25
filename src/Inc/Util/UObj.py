'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2020.02.21
License:     GNU, see LICENSE for more details
'''

def GetTree(aObj, aPrefix: str = '', aDepth: int = 99) -> list:
    Res = []

    Type = type(aObj).__name__
    if (aDepth > 0):
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
