'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2020.02.30
License:     GNU, see LICENSE for more details
Description: micropython ESP8266
'''

class TApiBase():
    Param = {}

    def Get(self, aData: dict, aKey: str):
        Def = self.Param.get(aKey)
        Val = aData.get(aKey)
        if (Val is None):
            Val = Def
        else:
            Type = type(Def)
            if (Type == int):
                Val = int(Val)
            elif (Type == float):
                Val = float(Val)
            elif (Type == bool):
                Val = bool(int(Val))
        return Val

    async def ExecDef(self, aData: dict, aParam: list):
        if (aData.get('debug')):
            print('debug', aData)
        else:
            Diff = set(list(aData.keys())) - set(list(self.Param.keys()) + ['r'])
            if (Diff):
                raise Exception('Unknown %s' % Diff)

        Arr = []
        for Param in aParam:
            Arr.append(self.Get(aData, Param))

        return await self.Exec(*Arr)

    async def Exec(self):
        raise NotImplementedError()
