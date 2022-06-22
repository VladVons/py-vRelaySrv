'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.21
License:     GNU, see LICENSE for more details
'''

from bs4 import BeautifulSoup
import json
import operator
import re
#
from IncP.Utils import GetMethodInfo, GetClassInfo, GetNestedKey, FilterMatch


_Whitespace = ' \t\n\r\v\f\xA0'
_Digits = '0123456789'
_DigitsDot = _Digits + '.'
_DigitsDotComma = _Digits + '.,'
#_XlatEntitles = [('&nbsp;', ' '), ('&lt;', '<'), ('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'")]

class TInStock():
    _Match = [
        'http://schema.org/instock',
        'https://schema.org/instock',

        'в наявності на складі',
        'в наявності',
        'до кошика',
        'додати у кошик',
        'є в наявності',
        'є на складі',
        'купити',
        'на складі',
        'товар в наявності',
        'товар є в наявності',
        'склад',

        'в корзину',
        'в наличии на складе',
        'в наличии',
        'добавить в корзину',
        'есть в наличии',
        'есть на складе',
        'есть',
        'купить',
        'на складе',
        'товар в наличии',
        'товар есть в наличии',
    ]

    _Del = [
        ' шт.'
    ]

    def __init__(self):
        self.Trans = str.maketrans('', '', _Digits)

    def Check(self, aVal: str) -> bool:
        aVal = aVal.translate(self.Trans).strip().lower()
        for Item in self._Del:
            aVal = aVal.replace(Item, '')
        return aVal in self._Match

InStock = TInStock()


def DigDelDecor(aVal: str) -> str:
# remove thousands decoration
    Pos = aVal.rfind('.')
    if (len(aVal) - Pos - 1 == 3):
       aVal = aVal.replace('.', '')
    return aVal

def DigSplit(aVal: str) -> tuple:
    Digit = ''
    Before = ''
    After = ''
    for x in aVal.rstrip('.'):
        if (x in _Whitespace):
            continue
        elif (After == '') and (x in _DigitsDotComma):
            if (x == ','):
                x = '.'
            Digit += x
        else:
            if (Digit):
                After += x
            else:
                Before += x
    Dots = Digit.count('.')
    if (Dots > 1):
        Digit = Digit.replace('.', '', Dots - 1)
    return (Before, DigDelDecor(Digit), After)


class TSchemeApi():
    def __new__(cls):
        raise TypeError('Cant instantiate static class')

    def strip(aVal: str) -> str:
        return aVal.strip()

    def strip_all(aVal: str) -> str:
        def Search(aData: str, aIter: list) -> int:
            for i in aIter:
                if (aData[i].isdigit() or aData[i].isalpha()):
                    return i
            return -1

        L = Search(aVal, range(len(aVal)))
        R = Search(aVal, range(len(aVal) - 1, L, -1))
        return aVal[L:R+1]

    def length(aVal: object) -> int:
        return len(aVal)

    def list(aVal: list, aIdx: int) -> object:
        if (aIdx < len(aVal)):
            return aVal[aIdx]

    def split(aVal: str, aDelim: str, aIdx: int = None) -> str:
        Res = aVal.split(aDelim)
        if (aIdx is not None):
            Res = Res[aIdx].strip()
        return Res

    def price(aVal: str) -> tuple:
        '''
        '''
        Before, Dig, After = DigSplit(aVal)
        if (not Dig):
            Dig = '0'
        return (float(Dig), After.lower())

    def stock(aVal: str) -> bool:
        '''
        Get stock availability.
        '''

        return InStock.Check(aVal)

    def image(aVal: BeautifulSoup) -> str:
        '''
        Get image.
        This equal to: find('img').get('src')
        '''

        Obj = aVal.find('img')
        if (Obj):
            return Obj.get('src')

    def is_equal(aVal: str, aStr: list) -> bool:
        '''
        Compare values
        '''
        return (aVal in aStr)

    def is_none(aVal: object, aTrue: bool = True) -> bool:
        '''
        Check if value is None
        '''

        return ((aVal is None) == aTrue)

    def search(aVal: object, aStr: list) -> bool:
        for x in aStr:
            if (aVal.find(x) >= 0):
                return True
        return False

    def compare(aVal: object, aOp: str, aValue = None) -> bool:
        Func = getattr(operator, aOp, None)
        if (Func):
            if (aValue is None):
                return Func(aVal)
            else:
                return Func(aVal, aValue)

    def dig_lat(aVal: str) -> str:
        Res = ''
        for x in aVal:
            if ('0' <= x <= '9') or ('a' <= x <= 'z') or ('A' <= x <= 'Z') or (x in '.-/'):
                Res += x
        return Res

    def txt2json(aVal: str) -> dict:
        return json.loads(aVal)

    def txt2float(aVal: str) -> float:
        return float(aVal.replace(',', ''))

    def json2txt(aVal: dict) -> str:
        return json.dumps(aVal, indent=2, sort_keys=True, ensure_ascii=False)

    def gets(aVal: dict, aKeys: str) -> dict:
        return GetNestedKey(aVal, aKeys)

    def breadcrumb(aVal: BeautifulSoup, aFind: list, aIdx: int = -1) -> str:
        if (hasattr(aVal, 'find_all')):
            Items = aVal.find_all(*aFind)
            if (len(Items) > 0):
               return Items[aIdx].text.strip()

    def app_json(aVal: BeautifulSoup, aFind: dict = {'@type': 'Product'}) -> dict:
        '''
        Searches value in sections <script>application/ld+json</script>
        '''
        Items = aVal.find_all('script', type='application/ld+json')
        for x in Items:
            Data = json.loads(x.text)
            Match = FilterMatch(Data, aFind)
            if (Match == aFind):
                return Data

    def lower(aVal: str) -> str:
        return aVal.lower()

    def replace(aVal: str, aFind: str, aRepl: str) -> str:
        return aVal.replace(aFind, aRepl)

    def translate(aVal: str, aFind: str, aRepl: str, aDel: str = None) -> str:
        return aVal.translate(aFind, aRepl, aDel)

    def left(aVal: str, aIdx: int) -> str:
        return aVal[:aIdx]

    def nop(aVal: object) -> object:
        '''
        No operation. For debug purpose
        '''
        return aVal

    def sub(aVal: str, aIdx: int, aEnd: int) -> str:
        return aVal[aIdx:aEnd]

    def unbracket(aVal: str, aPair: str = '()', aIdx: int = None) -> str:
        Pattern = '\%s(.*?)\%s' % (aPair[0], aPair[1])
        Res = re.findall(Pattern, aVal)
        if (Res):
            if (aIdx is not None):
                Res = Res[aIdx].strip()
            return Res

    def concat(aVal: str, aStr: str, aRight: bool =  True) -> str:
        if (aRight):
            Res = aVal + aStr
        else:
            Res = aStr + aVal
        return Res

    def print(aVal: object, aMsg: str = '') -> object:
        print(aVal, aMsg)
        return aVal

    def help(aVal: object) -> list:
        Data = GetClassInfo(TSchemeApi)
        return [x[2] for x in Data]

