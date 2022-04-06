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


def DigSplit(aValue: str) -> tuple:
    Digit = ''
    Before = '' 
    After = ''
    for x in aValue:
        if (x in _Invisible):
            continue
        elif (x in _Digits):
            Digit += x
        else:
            if (Digit): 
                After += x
            else:
                Before += x
    Res = (Before, Digit, After)
    return Res

def XlatReplace(aValue: str, aXlat: list) -> str:
    for Find, Replace in aXlat:
        aValue = aValue.replace(Find, Replace)
    return aValue


class TApi():
    @staticmethod
    def Strip(aValue: str) -> str:
        return aValue.strip()

    @staticmethod
    def List(aValue: list, aIdx: int) -> object:
        if (aIdx < len(aValue)):
            return aValue[aIdx]
    @staticmethod
    def Compare(aValue: str, aStr: str) -> bool:
        return (aValue in aStr.split('|'))

    @staticmethod
    def Split(aValue: str, aDelim: str = ' ', aIdx: int = 0) -> str:
        Arr = aValue.split(aDelim)
        if (aIdx <= len(aValue)):
            return Arr[aIdx].strip()

    @staticmethod
    def Price(aValue: str) -> tuple:
        Before, Dig, After = DigSplit(aValue) 
        if (not Dig):
            Dig = '0'
        return (float(Dig), After)        

    @staticmethod
    def DigLat(aValue: str) -> str:
        Res = ''
        for i in aValue:
            if ('0' <= i <= '9') or ('a' <= i <= 'z') or ('A' <= i <= 'Z') or (i in '.-/'):
                Res += i
        return Res


class TScheme():
    @staticmethod
    def Parse(aSoup, aData: dict) -> tuple:
        def GetItem(aObj, aScheme: list, aKey: str, aRes: tuple) -> object:
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
                        aRes[2].append('%s->%s' % (aKey, Item))
                        break
            return aObj

        Res = (dict(), set(), list())
        for Key, Val in aData.items():
            if (not Key.startswith('-')):
                if (Key.startswith('_Group')):
                    ValG = aData.get(Key, {})
                    R = GetItem(aSoup, ValG.get('_Path', []), Key, Res)
                    if (R):
                        R = TScheme.Parse(R, ValG.get('_Items', {}))
                        Res[0].update(R[0])
                        Res[1].update(R[1])
                        Res[2].append(R[2])
                else:
                    Res[1].add(Key)
                    R = GetItem(aSoup, Val, Key, Res)
                    if (R is not None):
                        Res[0][Key] = R
        return Res

    @staticmethod
    def ParseKeys(aSoup, aData: dict) -> dict:
        return {Key: TScheme.Parse(aSoup, Val) for Key, Val in aData.items() if (not Key.startswith('-'))}
