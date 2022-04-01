"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.01
License:     GNU, see LICENSE for more details
Description:

https://github.com/pythontoday/scrap_tutorial
"""


_Invisible = [' ', '\t', '\n', '\r', '\xA0']
_Digits = '0123456789.'


class TScheme():
    @staticmethod
    def Strip(aValue: str) -> str:
        return aValue.strip()

    @staticmethod
    def Dig(aValue: str) -> str:
        Res = ''
        for i in aValue:
            if (i in _Digits):
                Res += i
            elif (i == ','):
                Res += '.'
        return Res

    @staticmethod
    def DigLat(aValue: str) -> str:
        Res = ''
        for i in aValue:
            if ('0' <= i <= '9') or ('a' <= i <= 'z') or ('A' <= i <= 'Z') or (i in '.-/'):
                Res += i
        return Res

    @staticmethod
    def DigVis(aValue: str) -> str:
        Res = ''
        for i in aValue:
            if (i in _Digits):
                Res += i
            elif (i in _Invisible):
                continue
            else:
                break
        return Res

    @staticmethod
    def Parse(aObj, aSchema: dict) -> dict:
        Res = {}
        for SKey, SVal in aSchema.items():
            Obj = aObj
            for Val in SVal:
                ObjEx = getattr(TScheme, Val[0], None)
                if (ObjEx):
                    Obj = ObjEx(Obj)
                else:
                    Obj = getattr(Obj, Val[0])

                if (Obj is None):
                    break

                if (len(Val) > 1):
                    Obj = Obj(*Val[1])
                    #print('%10s %5s, %s' % (SKey, Obj != None, Val[1]))
                    if (Obj is None):
                        break
            if (Obj):
                Res[SKey] = Obj

        PathObj = Res.get('Path')
        if (PathObj):
            Data = TScheme.Parse(PathObj, aSchema.get('Dir', {}))
            del Res['Path']
            Res.update(Data)

        return Res
