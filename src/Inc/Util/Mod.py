# Created: 2022.03.21
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import sys
import re


def GetImportsLocal() -> set[str]: #//
    Res = set()
    for _Name, Val in globals().items():
        Type = type(Val).__name__
        if (Type == 'module'):
            Res.add(Val.__name__)
        elif (Type == 'type'):
            ModName = sys.modules[Val.__module__].__name__
            Res.add(ModName.split('.')[0])
    return Res

def GetImportsGlobal() -> set[str]: #//
    Res = set()
    for Name in sys.modules:
        if (not Name.startswith('_')):
            Res.add(Name.split('.')[0])
    return Res

def DynImport(aPath: str, aClass: str) -> object: #//
    try:
        Mod = __import__(aPath, None, None, [aClass])
        TClass = getattr(Mod, aClass, None)
    except ModuleNotFoundError as E:
        print(E)
    else:
        return TClass

#--- class methods help

def ParseFile(aFile: str) -> list: #//
    Res = []
    with open(aFile, 'r', encoding = 'utf-8') as File:
        for x in File.readlines():
            Method = re.findall(r'\s*def\s+(.*?):\s*$', x)
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
    Res = []
    for x in dir(aClass):
        Obj = getattr(aClass, x)
        if (not x.startswith('_') and hasattr(Obj, '__code__')):
            Res.append(GetMethod(Obj))
    return Res

def GetClassHelp(aModule: object, aClass: object) -> list[str]: #//
    FileInf = ParseFile(aModule.__file__)
    ClassInf = GetClass(aClass)
    for xClassInf in ClassInf:
        Inf = [y[0] for y in FileInf if y[0].startswith(xClassInf[0])]
        if (Inf):
            xClassInf.append(Inf[0])
        else:
            xClassInf.append('')
    return ClassInf

def GetModuleHelp(aModule: object) -> list[str]:
    return GetClassHelp(aModule, aModule)

#---
#http://www.qtrac.eu/pyclassmulti.html

def DAddMethods(aMethods: list):
    def Decor(aClass):
        for Method in aMethods:
            setattr(aClass, Method.__name__, Method)
        return aClass
    return Decor

def DAddModules(aModules: list, aSeparate: bool = False):
    def Decor(aClass):
        for Module in aModules:
            if (aSeparate):
                Name = Module.__name__.split('.')[-1]
                setattr(aClass, Name, Module)
            else:
                for Method in dir(Module):
                    if (not Method.endswith('__')):
                        Obj = getattr(Module, Method)
                        setattr(aClass, Method, Obj)
        return aClass
    return Decor

#---
