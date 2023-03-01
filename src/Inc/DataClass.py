# Created:     2022.10.22
# Author:      Vladimir Vons <VladVons@gmail.com>
# License:     GNU, see LICENSE for more details


'''
from Inc.DataClass import DDataClass, is_dataclass

@DDataClass
class TUser():
    Login: str
    Passw: str
    Allow: bool = True

@DDataClass
class TUserInherit(TUser):
    Age: int

User = TUser(Login = 'MyLogin', Passw = 'MyPassw')
print('asdict', User.asdict())
print('astuple', User.astuple())
print('str', str(User))
print('is_dataclass', is_dataclass(User))
'''

import sys


__all__ = ['DDataClass', 'asdict', 'astuple', 'is_dataclass']

_T = '_type_'
_D = '_dflt_'


def _Get(aCls, aName: str, aDef = None) -> object:
    if (hasattr(aCls, aName)):
        return getattr(aCls, aName)
    return aDef

def _Set(aCls, aDict: dict):
    for Key, Val in aDict.items():
        if (hasattr(aCls, Key)):
            setattr(aCls, Key, Val)

def is_dataclass(aCls) -> bool:
    return hasattr(aCls, 'astuple')

def asdict(aCls) -> dict:
    return aCls.__dict__

def astuple(aCls) -> dict:
    return [(Key, Val) for Key, Val in aCls.__dict__.items()]

def _Repr(aCls) -> str:
    Human = [f'{Key}={Val}' for Key, Val in aCls.__dict__.items()]
    return aCls.__class__.__name__ + '(' + ', '.join(Human) + ')'

def _GetArgs(aCls, aData: dict) -> str:
    Args = []
    for Name, Type in aData.items():
        if (Type.__module__ == 'builtins'):
            Param = f'{Name}: {Type.__name__}'
        else:
            Param = f'{Name}: {_T}{Name}'

        HasDefVal = hasattr(aCls, Name)
        if (HasDefVal):
            Param += f' = {_D}{Name}'
        Args.append(Param)
    return 'self, ' + ', '.join(Args)

def _Compile(aCls, aName: str, aData: dict):
    Body = []

    Wrapper = 'DecorWrapper'
    Body.append(f'def {Wrapper}():')

    if (aCls.__module__ in sys.modules):
        Globals = sys.modules[aCls.__module__].__dict__
    else:
        Globals = {}

    Args = _GetArgs(aCls, aData)
    Body.append(f' def {aName}({Args}):')
    for Name, Type in aData.items():
        NameK = f'{_T}{Name}'
        Globals[NameK] = Type

        HasDefVal = hasattr(aCls, Name)
        if (HasDefVal):
            Default = getattr(aCls, Name)
            NameK =f'{_D}{Name}'
            Globals[NameK] = Default

        Body.append(f'  self.{Name} = {Name}')
    Body.append(f' return {aName}')
    Body = '\n'.join(Body)

    Out = {}
    # pylint: disable-next=exec-used
    exec(Body, Globals, Out)
    Res = Out[Wrapper]()
    return Res

def _GetAnnotations(aCls):
    Res = {}
    for x in aCls.__mro__:
        Data = x.__dict__.get('__annotations__')
        if (Data):
            Res.update(Data)
    return Res

# Decorator
def DDataClass(aCls):
    Name = '__init__'
    #Annotations = aCls.__dict__.get('__annotations__')
    Annotations = _GetAnnotations(aCls)
    Data = _Compile(aCls, Name, Annotations)
    Data.__qualname__ = f'{aCls.__class__.__name__}.{Data.__name__}'
    setattr(aCls, Name, Data)

    aCls.__repr__ = _Repr
    setattr(aCls, 'get', _Get)
    setattr(aCls, 'set', _Set)
    setattr(aCls, 'asdict', asdict)
    setattr(aCls, 'astuple', astuple)
    return aCls
