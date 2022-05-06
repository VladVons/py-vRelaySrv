'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.01
License:     GNU, see LICENSE for more details
Description:

https://github.com/pythontoday/scrap_tutorial
'''


import re
import json
import operator
import enum
from Inc.Util.UObj import GetTree
from IncP.Utils import GetNestedKey


_Invisible = [' ', '\t', '\n', '\r', '\xA0']
_Digits = '0123456789.'
#_XlatEntitles = [('&nbsp;', ' '), ('&lt;', '<'), ('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'")]
_XlatKey = [('?', '')]


'''
_ReSpace = re.compile('\s+|\xA0')
_reSpace.split(aValue.strip())
        return Res
'''

class _If(enum.IntEnum):
    Sign = 0
    Script = 1
    Compare = 2
    ResTrue = 3
    ResFalse = 4

class _Res(enum.IntEnum):
    KeyVal = 0
    Keys = 1
    Err = 2


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
    def strip(aVal: str) -> str:
        return aVal.strip()

    @staticmethod
    def strip_all(aData: str) -> str:
        def Search(aData: str, aIter: list) -> int:
            for i in aIter:
                if (aData[i].isdigit() or aData[i].isalpha()):
                    return i
            return -1

        L = Search(aData, range(len(aData)))
        R = Search(aData, range(len(aData) - 1, L, -1))
        return aData[L:R+1]

    @staticmethod
    def list(aVal: list, aIdx: int) -> object:
        if (aIdx < len(aVal)):
            return aVal[aIdx]

    @staticmethod
    def equal(aVal: str, aStr: str) -> bool:
        return (aVal in aStr.split('|'))

    @staticmethod
    def compare(aObj: object, aOp: str, aValue = None) -> bool:
        Func = getattr(operator, aOp, None)
        if (Func):
            if (aValue is None):
                return Func(aObj)
            else:
                return Func(aObj, aValue)

    @staticmethod
    def split(aVal: str, aDelim: str, aIdx: int) -> str:
        Arr = aVal.split(aDelim)
        if (aIdx <= len(aVal)):
            return Arr[aIdx].strip()

    @staticmethod
    def price(aVal: str) -> tuple:
        Before, Dig, After = DigSplit(aVal)
        if (not Dig):
            Dig = '0'
        return (float(Dig), After)

    @staticmethod
    def dig_lat(aVal: str) -> str:
        Res = ''
        for x in aVal:
            if ('0' <= x <= '9') or ('a' <= x <= 'z') or ('A' <= x <= 'Z') or (x in '.-/'):
                Res += x
        return Res

    @staticmethod
    def json(aVal: str) -> dict:
        return json.loads(aVal)

    @staticmethod
    def gets(aData: dict, aKeys: str):
        return GetNestedKey(aData, aKeys)


class TSoupScheme():
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
    def GetItem(aObj, aItem: list, aRes: tuple, aPath: str = '') -> object:
        if (aItem[0].startswith('-')):
            return aObj

        Obj = getattr(TApi, aItem[0], None)
        if (Obj):
            Param = [aObj]
            if (len(aItem) == 2):
                Param += aItem[1]
            try:
                aObj = Obj(*Param)
            except Exception as E:
                aObj = None
                aRes[2].append('%s->%s %s' % (aPath, aItem, E))
        else:
            aObj = getattr(aObj, aItem[0], None)
            if (aObj):
                if (len(aItem) == 2):
                    aObj = aObj(*aItem[1])
            else:
                aRes[2].append('%s->%s unknown' % (aPath, aItem))

        if (aObj is None):
            if (not '?' in aPath):
                aRes[2].append('%s->%s' % (aPath, aItem))
        return aObj

    @staticmethod
    def GetItems(aObj, aScheme: list, aRes: tuple, aPath: str) -> object:
        i = 0
        while (i < len(aScheme)):
            if (type(aScheme[i]) != list):
                aRes[2].append('%s->%s not a list' % (aPath, aScheme[i]))
                return

            if (aScheme[i + _If.Sign][0] == '?'):
                R1 = TSoupScheme.GetItems(aObj, aScheme[i + _If.Script], aRes, aPath)
                R2 = TSoupScheme.GetItem(R1, aScheme[i + _If.Compare], aRes, aPath)
                Scheme = aScheme[i + _If.ResTrue + int(R2)]
                aObj = TSoupScheme.GetItems(aObj, Scheme, aRes, aPath)
                i += len(_If)
            else:
                aObj = TSoupScheme.GetItem(aObj, aScheme[i], aRes, aPath)
                if (aObj is None):
                    return
            i += 1
        return aObj

    @staticmethod
    def ParseItems(aSoup, aScheme: list, aRes: tuple, aPath: str, aKey: str) -> object:
        KeyPure = XlatReplace(aKey, _XlatKey)
        aRes[_Res.Keys].append(KeyPure)
        R = TSoupScheme.GetItems(aSoup, aScheme, aRes, aPath)
        if (R is not None):
            aRes[_Res.KeyVal][KeyPure] = R
        return R

    @staticmethod
    def Parse(aSoup, aData: dict, aPath: str = '') -> tuple:
        #KeyAndVal, Keys, Err
        Res = (dict(), list(), list())
        for Key, Val in aData.items():
            if (Key.startswith('-')):
                continue

            Path = aPath + '/' + Key
            if (Key.startswith('_Group')):
                ValG = aData.get(Key, {})
                Data = ValG.get('_Path')
                if (any(Data)):
                    R = TSoupScheme.GetItems(aSoup, Data, Res, Path)
                    if (R):
                        R = TSoupScheme.Parse(R, ValG.get('_Items', {}), Path)
                        Res[_Res.KeyVal].update(R[_Res.KeyVal])
                        Res[_Res.Keys].append(R[_Res.Keys])
                        Res[_Res.Err].append(R[_Res.Err])
            else:
                TSoupScheme.ParseItems(aSoup, Val, Res, Path, Key)
        return Res

    @staticmethod
    def ParseKeys(aSoup, aData: dict) -> dict:
        return {Key: TSoupScheme.Parse(aSoup, Val) for Key, Val in aData.items() if (not Key.startswith('-'))}
