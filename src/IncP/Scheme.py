"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.01
License:     GNU, see LICENSE for more details
Description:

https://github.com/pythontoday/scrap_tutorial
"""

import re

_Invisible = [' ', '\t', '\n', '\r', '\xA0']
_Digits = '0123456789.'
_XlatEntitles = [('&nbsp;', ' '), ('&lt;', '<'), ('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'")]


'''
_ReSpace = re.compile('\s+|\xA0')
_reSpace.split(aValue.strip())
        return Res
'''


def DigSplit(aVal: str) -> tuple:
    Digit = Before = After = ''
    for x in aVal:
        if (x in _Invisible):
            continue
        elif (x in _Digits):
            Digit += x
        else:
            if (Digit): 
                After += x
            else:
                Before += x
    return (Before, Digit, After)

def XlatReplace(aVal: str, aXlat: list) -> str:
    for Find, Replace in aXlat:
        aVal = aVal.replace(Find, Replace)
    return aVal


class TApi():
    @staticmethod
    def Strip(aVal: str) -> str:
        return aVal.strip()

    @staticmethod
    def List(aVal: list, aIdx: int) -> object:
        if (aIdx < len(aVal)):
            return aVal[aIdx]
 
    @staticmethod
    def Equal(aVal: str, aStr: str) -> bool:
        return (aVal in aStr.split('|'))

    @staticmethod
    def Split(aVal: str, aDelim: str = ' ', aIdx: int = 0) -> str:
        Arr = aVal.split(aDelim)
        if (aIdx <= len(aVal)):
            return Arr[aIdx].strip()

    @staticmethod
    def Price(aVal: str) -> tuple:
        Before, Dig, After = DigSplit(aVal) 
        if (not Dig):
            Dig = '0'
        return (float(Dig), After)        

    @staticmethod
    def DigLat(aVal: str) -> str:
        Res = ''
        for x in aVal:
            if ('0' <= x <= '9') or ('a' <= x <= 'z') or ('A' <= x <= 'Z') or (x in '.-/'):
                Res += x
        return Res


class TScheme():
    @staticmethod
    def Parse(aSoup, aData: dict, aPath: str = '') -> tuple:
        def GetItem(aObj, aScheme: list, aPath: str, aRes: tuple) -> object:
            for Item in aScheme:
                if (not Item[0].startswith('-')):
                    Obj = getattr(TApi, Item[0], None)
                    if (Obj):
                        Param = [aObj]
                        if (len(Item) == 2):
                            Param += Item[1]
                        aObj = Obj(*Param)
                    else:
                        aObj = getattr(aObj, Item[0], None)
                        if (aObj):
                            if (len(Item) == 2):
                                aObj = aObj(*Item[1])

                    if (aObj is None):
                        aRes[2].append('%s->%s' % (aPath, Item))
                        break
            return aObj

        Res = (dict(), list(), list())
        for Key, Val in aData.items():
            Path = aPath + '/' + Key
            if (not Key.startswith('-')):
                if (Key.startswith('_Group')):
                    ValG = aData.get(Key, {})
                    R = GetItem(aSoup, ValG.get('_Path', []), Path, Res)
                    if (R):
                        R = TScheme.Parse(R, ValG.get('_Items', {}), Path)
                        Res[0].update(R[0])
                        Res[1].append(R[1])
                        Res[2].append(R[2])
                else:
                    Res[1].append(Key)
                    R = GetItem(aSoup, Val, Path, Res)
                    if (R is not None):
                        Res[0][Key] = R
        return Res

    @staticmethod
    def ParseKeys(aSoup, aData: dict) -> dict:
        return {Key: TScheme.Parse(aSoup, Val) for Key, Val in aData.items() if (not Key.startswith('-'))}
