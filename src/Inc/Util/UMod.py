'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.21
License:     GNU, see LICENSE for more details
'''

import sys

def GetImportsLoc() -> set:
    Res = set()
    for Name, Val in globals().items():
        Type = type(Val).__name__
        if (Type == 'module'):
            Res.add(Val.__name__)
        elif (Type == 'type'):
            ModName = sys.modules[Val.__module__].__name__
            Res.add(ModName.split('.')[0])
    return Res

def GetImportsGlob() -> set:
    Res = set()
    for Name in sys.modules.keys():
        if (not Name.startswith('_')):
            Res.add(Name.split('.')[0])
    return Res

