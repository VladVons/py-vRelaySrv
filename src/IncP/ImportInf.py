'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.23
License:     GNU, see LICENSE for more details
'''


import re


def ParseFile(aFile: str) -> list:
    Res = []
    with open(aFile, 'r') as File:
        Res = []
        for x in File.readlines():
            Method = re.findall('\s*def\s+(.*?):\s*$', x)
            if (Method):
                Res.append(Method)
    return Res

def GetMethod(aObj) -> list:
    Name = aObj.__code__.co_name
    Args = aObj.__code__.co_varnames[:aObj.__code__.co_argcount]
    Repr = '%s(%s)' % (Name, ', '.join(Args))
    DocString = aObj.__doc__ if (aObj.__doc__) else ''
    return [Name, Args, Repr, DocString]

def GetClass(aClass: object) -> list:
    return [
        GetMethod(getattr(aClass, x))
        for x in dir(aClass)
        if (not x.startswith('__'))
    ]

def GetClassHelp(aModule: object, aClass: object) -> list:
    FileInf = ParseFile(aModule.__file__)
    ClassInf = GetClass(aClass)
    for x in ClassInf:
        Inf = [y[0] for y in FileInf if y[0].startswith(x[0])]
        if (Inf):
            x.append(Inf[0])
        else:
            x.append('')
    return ClassInf
