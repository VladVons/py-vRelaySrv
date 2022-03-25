'''
Author:      Vladimir Vons, Oster Inc.
Created:     2020.04.01
License:     GNU, see LICENSE for more details
Description:
'''


try:
  import asyncio
except:
  import uasyncio as asyncio
#
from Inc.Util.UObj import GetTree
from Inc.Util.UArr import SortLD
from Inc.KbdTerm  import TKbdTerm


class TMenu():
    async def AskYN(self, aMsg: str) -> bool:
        Str = await KbdTerm.Input('%s ?  Y/n:' % aMsg)
        return (Str) and (Str.lower() == 'y')

    def _ShowTree(self, aData: dict):
        for Var in SortLD(GetTree(aData), 'Key'):
            print('%15s = %s' % (Var['Key'], Var['Val']))

    async def WaitMsg(self, aMsg: str = '') -> str:
        return await KbdTerm.Input('%s (Press ENTER) ' % aMsg)

    async def Exec(self, aFunc, aParam: list):
        if (aParam):
            Data = await aFunc(*aParam)
        else:
            Data = await aFunc()

        self._ShowTree(Data)
        await self.WaitMsg()

    async def Parse(self, aPath: str, aItems: list):
        while True:
            print()
            print('Menu:', aPath)

            for Idx, (Name, Func, Param) in enumerate(aItems, 1):
                if (Param):
                    print('%2s %s %s' % (Idx, Name, Param))
                else:
                    if (Func):
                        print('%2s %s' % (Idx, Name))
                    else:
                        print('%2s %s' % (' ', Name))
            if (not aItems):
                await self.WaitMsg('No items')
                break

            print(' 0', 'Exit')
            Str = await KbdTerm.Input('Enter choice: ')
            if (Str == '') or (Str == '0') or (not Str.isdigit()):
                break

            Idx = int(Str)
            if (Idx > len(aItems)):
                await self.WaitMsg('Out of range')
                continue
            else:
                Name, Func, Param = aItems[Idx - 1]
                if (Func):
                    await Func(aPath + '/' + Name, Param)

    async def Input(self, aItems: dict, aDef: dict = {}) -> dict:
        R = {}

        Title, Items = aItems
        print()
        print('-', Title, '-')

        for Idx, (Name, Text, ValDef) in enumerate(Items, 1):
            ValDef = aDef.get(Name, ValDef)
            Last = Text[-1]
            while True:
                Val = await KbdTerm.Input('%s/%s) %s [%s]:' % (Idx, len(Items), Text, ValDef))
                if (Val == '-'):
                    Val = ''
                elif (not Val) and (ValDef):
                    Val = ValDef

                if (Last != '*') or ((Last == '*') and (Val)):
                    break

            Type = type(ValDef).__name__
            if (Type == 'int'):
                Val = int(Val)
            elif (Type == 'float'):
                Val = float(Val)

            R[Name] = Val
        return R

    async def Run(self, aKey: str):
        Msg = 'Press `%s` to enter menu' % (aKey)
        print(Msg)

        while True:
            Key = KbdTerm.GetChr()
            if (Key == aKey):
                await self.DoRun()
                print(Msg)
            else:
                await asyncio.sleep(0.5)

    async def DoRun(self):
        raise NotImplementedError()


KbdTerm = TKbdTerm()
