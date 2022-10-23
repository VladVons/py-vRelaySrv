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
'''


def _GetArgs(aCls, aData: dict) -> str:
    Args = []
    for Name, Type in aData.items():
        Param = f'{Name}: {Type.__name__}'
        Default = getattr(aCls, Name, None)
        if (Default is not None):
            if (Type == str):
                Default = '"' + Default + '"'
            Param += f' = {Default}'
        Args.append(Param)
    return 'self, ' + ', '.join(Args)

def _Compile(aCls, aName: str, aData: dict):
    Body = []

    Wrapper = 'Wrapper'
    Body.append(f'def {Wrapper}():')

    Args = _GetArgs(aCls, aData)
    Body.append(f' def {aName}({Args}):')
    for Name, _Type in aData.items():
        Body.append(f'  self.{Name} = {Name}')
    Body.append(f' return {aName}')

    Out = {}
    exec('\n'.join(Body), {}, Out)
    Res = Out[Wrapper]()
    return Res

# decorator
def DataClass(aCls):
    Name = '__init__'
    Annotations = aCls.__dict__.get('__annotations__', {})
    Data = _Compile(aCls, Name, Annotations)
    Data.__qualname__ = f'{aCls.__class__.__name__}.{Data.__name__}'
    setattr(aCls, Name, Data)
    return aCls
