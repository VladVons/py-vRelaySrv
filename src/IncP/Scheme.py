'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.01
License:     GNU, see LICENSE for more details

https://github.com/pythontoday/scrap_tutorial
'''

from bs4 import BeautifulSoup
import datetime
import json
import random
import re
import sys
#
from IncP.Python import TPython
from IncP.SchemeApi import TSchemeApi
from IncP.Utils import GetNestedKey, FilterKey, FilterKeyErr


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



def SoupGetParents(aSoup: BeautifulSoup, aItems: list, aDepth: int = 99) -> list:
    Res = []
    for Item in aItems:
        Depth = aDepth
        ResLoop = []
        while (Item) and (Item != aSoup) and (Depth > 0):
            Attr = getattr(Item, 'attrs', None)
            if (Attr):
                ResLoop.append([Item.name, Attr])
            elif (Item.name):
                ResLoop.append([Item.name, {}])
            else:
                if (type(Item).__name__ == 'Script'):
                    break
                ResLoop.append([Item, {}])
            Depth -= 1

            Item = Item.parent
        Res.append(ResLoop)
    return Res

def SoupFindParents(aSoup: BeautifulSoup, aSearch: str) -> list:
    #Items = aSoup.findAll(string=aSearch)
    Items = aSoup.findAll(string=re.compile(aSearch))
    return SoupGetParents(aSoup, Items)

class TSoupScheme():
    def __init__(self):
        self.Debug = False
        self.Clear()

    def Clear(self):
        self.Err = []
        self.Warn = []
        self.Var = {}

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
        Name = aItem[0]
        Obj = getattr(TSchemeApi, Name, None)
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
            if (self.Debug) and (Name == 'find'):
                if (hasattr(aObj, 'find_all')) and (len(aItem) == 2):
                    Arr = aObj.find_all(*aItem[1])
                    if (len(Arr) > 1):
                        Parents = SoupGetParents(aObj, Arr, 2)
                        self.Warn.append('%s -> %s (found %s)' % (aPath, aItem[1], len(Arr)))
                        for x in Parents:
                            self.Warn.append(str(x))

            aObj = getattr(aObj, Name, None)
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

            Macro = Scheme[0]
            if (not Macro.startswith('-')):
                aPath += '/' + Scheme[0]
                if (Macro == 'as_if'):
                    R = self.ParsePipes(aObj, Scheme[1].get('cond', []), aPath)
                    Cond = str(R is not None).lower()
                    aObj = self.ParsePipes(aObj, Scheme[1].get(Cond), aPath)
                elif (Macro == 'as_list'):
                    aObj = [self.ParsePipes(aObj, x, aPath) for x in Scheme[1]]
                elif (Macro == 'as_dict'):
                    aObj = {
                        Key: self.ParsePipes(aObj, Val, aPath + '/' + Key)
                        for Key, Val in Scheme[1].items()
                        if (not Key.startswith('-') and (Val))
                    }
                else:
                    if (Macro.startswith('$')):
                        aObj = self.Var.get(Macro)
                        if (not aObj):
                            self.Err.append('%s (unknown)' % (aPath))
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
                    if (Key.startswith('$')):
                        self.Var[Key] = self.ParsePipes(aSoup, Val, Path)
                    elif Key.startswith('Pipe'):
                        Res[Key] = self.ParsePipes(aSoup, Val, Path)
                    else:
                        Res[Key] = self._ParseRecurs(aSoup, Val, Path)
        elif (Type == list):
            if (aData[0].startswith('$')):
                Res = self.ParseMacro(aData, aPath)
            else:
                Res = [self._ParseRecurs(aSoup, Val, aPath) for Val in aData]
        else:
            Res = aData
        return Res

    def Parse(self, aSoup, aData: dict) -> dict:
        self.Clear()
        Res = self._ParseRecurs(aSoup, aData, '')
        return Res


class TSchemePy():
    def __init__(self, aScheme: str):
        self.Python = TPython(aScheme)
        self.Python.Compile()
        self.Clear()

    def Parse(self, aSoup):
        self.Clear()

        if (aSoup):
            Param = {'aVal': aSoup, 'aApi': TSchemeApi, 'aRes': TRes, 'aPy': self.Python}
            Res = self.Python.Exec(Param)
            Err = FilterKeyErr(Res)
            if (Err):
                self.Err = Res.get('Data')
            else:
                Data = Res.get('Data')
                self.Data = Data.get('Data', {})
                self.Err = Data.get('Err', [])

                self.Pipe = FilterKey(self.Data, self.GetFields(), dict)
        return self

    def GetUrl(self) -> list:
        #Match = re.search('Url\s*=\s*(.*?)$', self.Scheme, re.DOTALL)
        Match = re.search("(?P<url>http[s]?://[^\s]+)", self.Python.Script, re.DOTALL)
        if (Match):
            return [Match.group('url')]


class TSchemeJson():
    def __init__(self, aScheme: str):
        self.Debug = False
        self.Scheme = json.loads(aScheme)
        self.Clear()

    def Parse(self, aSoup):
        self.Clear()
        if (aSoup):
            SoupScheme = TSoupScheme()
            SoupScheme.Debug = self.Debug
            self.Data = SoupScheme.Parse(aSoup, self.Scheme)
            self.Err = SoupScheme.Err
            self.Warn = SoupScheme.Warn

            self.Pipe = FilterKey(self.Data, self.GetFields(), dict)
        return self

    def GetUrl(self) -> list:
        return GetNestedKey(self.Scheme, 'Product.Info.Url')


def TScheme(aScheme: str):
    if ('aApi.' in aScheme):
        Class = TSchemePy
    else:
        Class = TSchemeJson

    class TClass(Class):
        def IsJson(self) -> bool:
            #Name = self.__class__.__bases__[0].__name__
            return self.__class__.__bases__[0] == TSchemeJson

        def Clear(self):
            self.Data = {}
            self.Pipe = {}
            self.Err = []
            self.Warn = []

        def GetData(self, aKeys: list = []) -> dict:
            Res = {'Data': self.Data, 'Err': self.Err, 'Pipe': self.Pipe, 'Warn': self.Warn}
            if (aKeys):
                Res = {Key: Res.get(Key) for Key in aKeys}
            return Res

        def GetFields(self) -> list:
            return ['image', 'price', 'price_old', 'name', 'stock', 'mpn', 'category']

        def GetPipe(self) -> dict:
            return {Key.split('.')[-1]: Val for Key, Val in self.Pipe.items()}

    return TClass(aScheme)
