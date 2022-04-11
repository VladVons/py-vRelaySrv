"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.01
License:     GNU, see LICENSE for more details
Description:

https://github.com/pythontoday/scrap_tutorial
"""

import re
from Inc.Util.UObj import GetTree

_Invisible = [' ', '\t', '\n', '\r', '\xA0']
_Digits = '0123456789.'
#_XlatEntitles = [('&nbsp;', ' '), ('&lt;', '<'), ('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'")]
_XlatKey = [('?', '')]


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
    def GetParents(aSoup, aSearch: str) -> list:
        ResAll = []
        #Items = aSoup.findAll(string=aSearch)
        Items = aSoup.findAll(string=re.compile(aSearch))

        for Item in Items:
            Res = []
            while (Item) and (Item != aSoup):
                Attr = getattr(Item, 'attrs', None)
                if (Attr):
                    Res.append([Item.name, Attr])
                elif (Item.name):
                    Res.append([Item.name, {}])
                else:
                    if (type(Item).__name__ == 'Script'): 
                        break
                    Res.append([Item, {}])

                Item = Item.parent
            ResAll.append(Res)
        return ResAll

    @staticmethod
    def GetItem(aObj, aScheme: list, aRes: tuple, aPath: str = '') -> object:
        for Item in aScheme:
            if (type(Item).__name__ != 'list'):
                aRes[2].append('%s->%s. Not a list' % (aPath, Item))
                return     
            
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
                    if (not '?' in aPath):
                        aRes[2].append('%s->%s' % (aPath, Item))
                    break
        return aObj

    @staticmethod
    def Parse(aSoup, aData: dict, aPath: str = '') -> tuple:
        Res = (dict(), list(), list())
        for Key, Val in aData.items():
            Path = aPath + '/' + Key
            if (not Key.startswith('-')):
                if (Key.startswith('_Group')):
                    ValG = aData.get(Key, {})
                    _Path = ValG.get('_Path')
                    if (any(_Path)):
                        R = TScheme.GetItem(aSoup, _Path, Res, Path)
                        if (R):
                            R = TScheme.Parse(R, ValG.get('_Items', {}), Path)
                            Res[0].update(R[0])
                            Res[1].append(R[1])
                            Res[2].append(R[2])
                else:
                    KeyPure = XlatReplace(Key, _XlatKey)
                    Res[1].append(KeyPure)
                    R = TScheme.GetItem(aSoup, Val, Res, Path)
                    if (R is not None):
                        Res[0][KeyPure] = R
        return Res

    @staticmethod
    def ParseKeys(aSoup, aData: dict) -> dict:
        return {Key: TScheme.Parse(aSoup, Val) for Key, Val in aData.items() if (not Key.startswith('-'))}
