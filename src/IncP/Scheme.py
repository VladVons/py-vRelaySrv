'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.01
License:     GNU, see LICENSE for more details
Description:

https://github.com/pythontoday/scrap_tutorial
'''

import sys
import re
import json
import operator
import datetime
import random

#
from Inc.Util.UObj import GetTree
from IncP.Utils import GetNestedKey, GetMethodInfo
from IncP.Python import TPython
from IncP.Log import Log, _GetStack


_InStock = [
    'http://schema.org/instock',
    'https://schema.org/instock',

    'в наявності',
    'в наявності на складі',
    'є в наявності',
    'купити',
    'на складі',
    'товар в наявності',

    'в наличии на складе',
    'в наличии',
    'добавить в корзину',
    'есть в наличии',
    'есть',
    'купить',
    'на складе',
]

_Invisible = [' ', '\t', '\n', '\r', '\xA0']
_Digits = '0123456789.'
#_XlatEntitles = [('&nbsp;', ' '), ('&lt;', '<'), ('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'")]


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

class TRes():
    def __init__(self, aScheme):
        self.Scheme = aScheme
        self.Clear()

    def Clear(self):
        self.Data = {}
        self.Err = []

    def Exec(self, aPrefix: str, aPy: TPython):
        self.Clear()

        Obj = getattr(self, aPrefix, None)
        if (Obj is None):
            self.Err.append('No method %s' % aPrefix)
            return

        PrefixData = Obj(self.Scheme)
        if (PrefixData is None):
            self.Err.append('Empty data returned %s' % Name)
            return

        Keys = [Key for Key in dir(self) if (Key.startswith(aPrefix)) and Key != aPrefix]
        for Key in Keys:
            Obj = getattr(self, Key, None)
            Name = Key.replace(aPrefix, '')
            if callable(Obj):
                try:
                    Res = Obj(PrefixData)
                    if (Res is None):
                        self.Add(Name, Res, '(none)')
                    else:
                        self.Add(Name, Res)
                except Exception as E:
                    Err = aPy.ErrMsg(E, sys.exc_info())
                    self.Add(Name, None, Err)

    def Add(self, aKey: str, aVal: object, aErr: str = None):
        self.Data[aKey] = aVal
        if (aErr):
            self.Err.append('%s %s' % (aKey, aErr))

class TApiMacro():
    @staticmethod
    def date() -> str:
        return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    @staticmethod
    def rand(aStart: int, aEnd: int) -> int:
        return random.randint(aStart, aEnd)

    @staticmethod
    def prop(aMod: str, aProp: str, aDef = None) -> object:
        __import__(aMod)
        Mod = sys.modules.get(aMod)
        return getattr(Mod, aProp, aDef)


class TApi():
    @staticmethod
    def strip(aVal: str) -> str:
        return aVal.strip()

    @staticmethod
    def strip_all(aVal: str) -> str:
        def Search(aData: str, aIter: list) -> int:
            for i in aIter:
                if (aData[i].isdigit() or aData[i].isalpha()):
                    return i
            return -1

        L = Search(aVal, range(len(aVal)))
        R = Search(aVal, range(len(aVal) - 1, L, -1))
        return aVal[L:R+1]

    @staticmethod
    def list(aVal: list, aIdx: int) -> object:
        if (aIdx < len(aVal)):
            return aVal[aIdx]

    @staticmethod
    def equal(aVal: str, aStr: str, aDelim: str = '|') -> bool:
        Arr = aStr.split(aDelim)
        return (aVal in Arr)

    @staticmethod
    def search(aVal: object, aStr: str, aDelim: str = '|') -> bool:
        for x in aStr.split(aDelim):
            if (aVal.find(x) >= 0):
                return True
        return False

    @staticmethod
    def compare(aVal: object, aOp: str, aValue = None) -> bool:
        Func = getattr(operator, aOp, None)
        if (Func):
            if (aValue is None):
                return Func(aVal)
            else:
                return Func(aVal, aValue)

    @staticmethod
    def split(aVal: str, aDelim: str, aIdx: int = None) -> str:
        Res = aVal.split(aDelim)
        if (aIdx is not None):
            Res = Res[aIdx].strip()
        return Res

    @staticmethod
    def price(aVal: str) -> tuple:
        Before, Dig, After = DigSplit(aVal)
        if (not Dig):
            Dig = '0'
        return (float(Dig), After)

    @staticmethod
    def stock(aVal: str, aWords: list = _InStock) -> bool:
        return aVal.strip().lower() in aWords

    @staticmethod
    def image(aVal: object) -> str:
        Obj = aVal.find('img')
        if (Obj):
            return Obj.get('src')

    @staticmethod
    def dig_lat(aVal: str) -> str:
        Res = ''
        for x in aVal:
            if ('0' <= x <= '9') or ('a' <= x <= 'z') or ('A' <= x <= 'Z') or (x in '.-/'):
                Res += x
        return Res

    @staticmethod
    def txt2json(aVal: str) -> dict:
        return json.loads(aVal)

    @staticmethod
    def txt2float(aVal: str) -> float:
        return float(aVal.replace(',', ''))

    def json2xt(aVal: dict) -> str:
        return json.dumps(aVal, indent=2, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def gets(aVal: dict, aKeys: str) -> dict:
        return GetNestedKey(aVal, aKeys)

    @staticmethod
    def lower(aVal: str) -> str:
        return aVal.lower()

    @staticmethod
    def replace(aVal: str, aFind: str, aRepl: str) -> str:
        return aVal.replace(aFind, aRepl)

    @staticmethod
    def translate(aVal: str, aFind: str, aRepl: str, aDel: str = None) -> str:
        return aVal.translate(aFind, aRepl, aDel)

    @staticmethod
    def left(aVal: str, aIdx: int) -> str:
        return aVal[:aIdx]

    @staticmethod
    def sub(aVal: str, aIdx: int, aEnd: int) -> str:
        return aVal[aIdx:aEnd]

    @staticmethod
    def unbracket(aVal: str, aPair: str = '()', aIdx: int = None) -> str:
        Pattern = '\%s(.*?)\%s' % (aPair[0], aPair[1])
        Res = re.findall(Pattern, aVal)
        if (Res):
            if (aIdx is not None):
                Res = Res[aIdx].strip()
            return Res

    @staticmethod
    def concat(aVal: str, aStr: str, aRight: bool =  True) -> str:
        if (aRight):
            Res = aVal + aStr
        else:
            Res = aStr + aVal
        return Res

    @staticmethod
    def print(aVal: object, aMsg: str = '') -> object:
        print(aVal, aMsg)
        return aVal

    def help(aVal: object) -> list:
        Res = [
            GetMethodInfo(getattr(TApi, x))[2]
            for x in dir(TApi)
            if (not x.startswith('__'))
        ]
        return Res


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

    # Syntax ["$date"], ["$rand", [1, 10]], ["$prop", ["IncP", "__version__"]]
    def ParseMacro(self, aItem: list, aPath: str) -> object:
        Func = getattr(TApiMacro, aItem[0][1:], None)
        if (Func):
            try:
                if (len(aItem) > 1):
                    Res = Func(*aItem[1])
                else:
                    Res = Func()
            except Exception as E:
                Res = aItem
                self.Err.append('%s->%s %s (exception)' % (aPath, aItem[0], E))
        else:
            Res = aItem
            self.Err.append('%s->%s (unknown)' % (aPath, aItem))
        return Res

    def ParsePipe(self, aObj, aItem: list, aPath: str) -> object:
        Obj = getattr(TApi, aItem[0], None)
        if (Obj):
            Param = [aObj]
            if (len(aItem) == 2):
                Param += aItem[1]
            try:
                aObj = Obj(*Param)
            except Exception as E:
                self.Err.append('%s->%s %s (exception)' % (aPath, aItem, E))
                return
        else:
            aObj = getattr(aObj, aItem[0], None)
            if (aObj):
                if (len(aItem) == 2):
                    try:
                        aObj = aObj(*aItem[1])
                    except Exception as E:
                        self.Err.append('%s->%s %s (exception)' % (aPath, aItem, E))
                        return
            else:
                self.Err.append('%s->%s (unknown)' % (aPath, aItem))
                return

        if (aObj is None):
            self.Err.append('%s->%s (none)' % (aPath, aItem))
        return aObj

    def ParsePipes(self, aObj, aScheme: list, aPath: str) -> object:
        i = 0
        while (aObj) and (i < len(aScheme)):
            Scheme = aScheme[i]
            if (type(Scheme) != list):
                self.Err.append('%s->%s (not a list)' % (aPath, Scheme))
                return

            q1 = Scheme[0]
            if (not Scheme[0].startswith('-')):
                aPath += '/' + Scheme[0]
                if (Scheme[0] == 'as_if'):
                    R = self.ParsePipes(aObj, Scheme[1].get('cond', []), aPath)
                    Cond = str(R is not None).lower()
                    aObj = self.ParsePipes(aObj, Scheme[1].get(Cond), aPath)
                elif (Scheme[0] == 'as_list'):
                    aObj = [self.ParsePipes(aObj, x, aPath) for x in Scheme[1]]
                elif (Scheme[0] == 'as_dict'):
                    aObj = {
                        Key: self.ParsePipes(aObj, Val, aPath)
                        for Key, Val in Scheme[1].items()
                        if (not Key.startswith('-') and (Val))
                    }
                else:
                    aObj = self.ParsePipe(aObj, Scheme, aPath)
            i += 1
        return aObj

    def _ParseRecurs(self, aSoup, aData: dict, aPath: str) -> dict:
        Type = type(aData)
        if (Type == dict):
            Res = {}
            for Key, Val in aData.items():
                if (not Key.startswith('-')):
                    Path = aPath + '/' + Key
                    if Key.startswith('Pipe'):
                        R = self.ParsePipes(aSoup, Val, Path)
                    else:
                        R = self._ParseRecurs(aSoup, Val, Path)
                    Res[Key] = R
        elif (Type == list):
            if (aData[0].startswith('$')):
                Res = self.ParseMacro(aData, aPath)
            else:
                Res = [self._ParseRecurs(aSoup, Val, aPath) for Val in aData]
        else:
            Res = aData
        return Res

    def Parse(self, aSoup, aData: dict) -> dict:
        self.Err = []
        return self._ParseRecurs(aSoup, aData, '')


class TSchemePy():
    def __init__(self, aScheme: str):
        self.Python = TPython(aScheme)
        self.Python.Compile()
        self.Clear()

    def Parse(self, aSoup):
        self.Clear()

        if (aSoup):
            Param = {'aVal': aSoup, 'aApi': TApi(), 'aRes': TRes, 'aPy': self.Python}
            Res = self.Python.Exec(Param)
            if (Res.get('Err')):
                self.Err = Res.get('Err')
            else:
                Data = Res.get('Data')
                self.Data = Data.get('Data', {})
                self.Err = Data.get('Err', [])

                Keys = ['Image', 'Price', 'PriceOld', 'Name', 'Stock', 'MPN']
                self._FilterRecurs(self.Data, Keys, self.Pipe) 
        return self


    def GetUrl(self) -> str:
        #Match = re.search('Url\s*=\s*(.*?)$', self.Scheme, re.DOTALL)
        Match = re.search("(?P<url>http[s]?://[^\s]+)", self.Python.Script, re.DOTALL)
        if (Match):
            return Match.group('url')


class TSchemeJson():
    def __init__(self, aScheme: str):
        self.Scheme = json.loads(aScheme)
        self.Clear()

    def Parse(self, aSoup):
        self.Clear()
        if (aSoup):
            SoupScheme = TSoupScheme()
            self.Data = SoupScheme.Parse(aSoup, self.Scheme)
            self.Err = SoupScheme.Err

            Keys = ['Image', 'Price', 'PriceOld', 'Name', 'Stock', 'MPN']
            self._FilterRecurs(self.Data, Keys, self.Pipe)
        return self

    def GetUrl(self) -> str:
        return GetNestedKey(self.Scheme, 'Product.Info.Url', '')


def TScheme(aScheme: str):
    if ('aApi.' in aScheme):
        Class = TSchemePy
    else:
        Class = TSchemeJson

    class TClass(Class):
        def _FilterRecurs(self, aData: object, aKeys: list, aRes: dict):
            if (type(aData) == dict):
                for Key, Val in aData.items():
                    self._FilterRecurs(Val, aKeys, aRes)
                    if (Key in aKeys):
                        aRes[Key] = Val

        def IsJson(self):
            #Name = self.__class__.__bases__[0].__name__
            return self.__class__.__bases__[0] == TSchemeJson

        def Clear(self):
            self.Data = {}
            self.Err = []
            self.Pipe = {}

        def GetData(self, aKeys: list = []):
            Res = {'Data': self.Data, 'Err': self.Err, 'Pipe': self.Pipe}
            if (aKeys):
                Res = {Key: Res.get(Key) for Key in aKeys}
            return Res

    return TClass(aScheme)
