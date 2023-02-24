# Created:     2022.10.22
# Author:      Vladimir Vons <VladVons@gmail.com>
# License:     GNU, see LICENSE for more details


'''
from DataClass import DataClass

@DataClass
class TUser():
    Login: str
    Passw: str
    Allow: bool = True

User = TUser(Login = 'MyLogin', Passw = 'MyPassw')
print(User.__dict__)
print(User)
'''


import sys


__all__ = ['DataClass', 'asdict', 'astuple']

_T = '_Type'

def _Get(aCls, aName: str, aDef = None) -> object:
    if (hasattr(aCls, aName)):
        return getattr(aCls, aName)
    return aDef

def _Set(aCls, aDict: dict):
    for Key, Val in aDict.items():
        if (hasattr(aCls, Key)):
            setattr(aCls, Key, Val)

def asdict(aCls) -> dict:
    return aCls.__dict__

def astuple(aCls) -> dict:
    return list(aCls.__dict__)

def _Repr(aCls) -> str:
    Human = [f'{Key}={Val}' for Key, Val in aCls.__dict__.items()]
    return aCls.__class__.__name__ + '(' + ', '.join(Human) + ')'

def _GetArgs(aCls, aData: dict) -> str:
    Args = []
    for Name, Type in aData.items():
        if (Type.__module__ == 'builtins'):
            Param = f'{Name}: {Type.__name__}'
        else:
            #Param = f'{Name}: {Type.__module__}.{Type.__name__}'
            Param = f'{Name}: {_T}{Name}'

        Uniq = 'q1S4t6G7x'
        Default = getattr(aCls, Name, Uniq)
        if (Default != Uniq):
            if (Type == str):
                Default = '"' + Default + '"'
            Param += f' = {Default}'
        Args.append(Param)
    return 'self, ' + ', '.join(Args)

def _Compile(aCls, aName: str, aData: dict):
    Body = []

    Wrapper = 'Wrapper'
    Body.append(f'def {Wrapper}():')

    if (aCls.__module__ in sys.modules):
        Globals = sys.modules[aCls.__module__].__dict__
    else:
        Globals = {}

    Args = _GetArgs(aCls, aData)
    Body.append(f' def {aName}({Args}):')
    for Name, Type in aData.items():
        NameT = f'{_T}{Name}'
        Globals[NameT] = Type
        Body.append(f'  self.{Name} = {Name}')
    Body.append(f' return {aName}')
    Body = '\n'.join(Body)

    Out = {}
    # pylint: disable-next=exec-used
    exec(Body, Globals, Out)
    Res = Out[Wrapper]()
    return Res

# decorator
def DataClass(aCls):
    Name = '__init__'
    Annotations = aCls.__dict__.get('__annotations__', {})
    Data = _Compile(aCls, Name, Annotations)
    Data.__qualname__ = f'{aCls.__class__.__name__}.{Data.__name__}'
    setattr(aCls, Name, Data)

    aCls.__repr__ = _Repr
    setattr(aCls, 'get', _Get)
    setattr(aCls, 'set', _Set)
    setattr(aCls, 'asdict', asdict)
    setattr(aCls, 'astuple', astuple)
    return aCls
