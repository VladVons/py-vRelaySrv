'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.06.21
License:     GNU, see LICENSE for more details
'''

import json
import operator
import re
from bs4 import BeautifulSoup
#
from IncP.Utils import GetNestedKey, FilterMatch
from IncP.ImportInf import GetClass


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

    @staticmethod
    def strip(aVal: str) -> str:
        '''
        remove invisible chars
        ["strip"]
        '''

        return aVal.strip()

    @staticmethod
    def strip_all(aVal: str) -> str:
        '''
        remove all invisible chars
        ["strip_all"]
        '''

        def Search(aData: str, aIter: list) -> int:
            for i in aIter:
                if (aData[i].isdigit() or aData[i].isalpha()):
                    return i
            return -1

        L = Search(aVal, range(len(aVal)))
        R = Search(aVal, range(len(aVal) - 1, L, -1))
        return aVal[L:R+1]

    @staticmethod
    def length(aVal: object) -> int:
        '''
        get object length
        ["length"]
        '''

        return len(aVal)

    @staticmethod
    def list(aVal: list, aIdx: int) -> object:
        '''
        get object from list by index
        ["list", [1]]
        '''

        if (aIdx < len(aVal)):
            return aVal[aIdx]

    @staticmethod
    def split(aVal: str, aDelim: str, aIdx: int = None) -> str:
        '''
        split string by delimiter and get object from list by index
        ["split", [" ", -1]]
        '''

        Res = aVal.split(aDelim)
        if (aIdx is not None):
            Res = Res[aIdx].strip()
        return Res

    @staticmethod
    def price(aVal: str) -> tuple:
        '''
        get price
        ["price"]
        '''

        Before, Dig, After = DigSplit(aVal)
        if (not Dig):
            Dig = '0'
        return (float(Dig), After.lower())

    @staticmethod
    def stock(aVal: str) -> bool:
        '''
        Get stock availability
        ["stock"]
        '''

        return InStock.Check(aVal)

    @staticmethod
    def image(aVal: BeautifulSoup) -> str:
        '''
        get image. equal to: find('img').get('src')
        ["image"]
        '''

        Obj = aVal.find('img')
        if (Obj):
            return Obj.get('src')

    @staticmethod
    def is_equal(aVal: str, aStr: list) -> bool:
        '''
        compare values
        ["is_equal", ["InStock", "available"]]
        '''

        return (aVal in aStr)

    @staticmethod
    def is_none(aVal: object, aTrue: bool = True) -> bool:
        '''
        check if value is None
        ["is_none", false]
        '''

        return ((aVal is None) == aTrue)

    @staticmethod
    def search(aVal: object, aStr: list) -> bool:
        '''
        search any string value from a list
        ["search", ["InStock", "available"]]
        '''

        for x in aStr:
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
    def dig_lat(aVal: str) -> str:
        '''
        get filtered chars from [0..9], [a..Z], [.-/]
        ["dig_lat"]
        '''

        Res = ''
        for x in aVal:
            if ('0' <= x <= '9') or ('a' <= x <= 'z') or ('A' <= x <= 'Z') or (x in '.-/'):
                Res += x
        return Res

    @staticmethod
    def txt2json(aVal: str) -> dict:
        '''
        convert text to json
        ["txt2json"]
        '''

        return json.loads(aVal)

    @staticmethod
    def txt2float(aVal: str) -> float:
        '''
        convert text to float
        ["txt2float"]
        '''

        return float(aVal.replace(',', ''))

    @staticmethod
    def json2txt(aVal: dict) -> str:
        '''
        convert json to text
        ["json2txt"]
        '''

        return json.dumps(aVal, indent=2, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def gets(aVal: dict, aKeys: str) -> dict:
        '''
        multiple get. equal to get('key1').get('key2')
        ["gets", ["offers.availability"]]
        '''

        return GetNestedKey(aVal, aKeys)

    @staticmethod
    def breadcrumb(aVal: BeautifulSoup, aFind: list, aIdx: int = -1) -> str:
        '''
        equal to find_all() + list()
        ["breadcrumb", [["a"], -1]]
        '''

        if (hasattr(aVal, 'find_all')):
            Items = aVal.find_all(*aFind)
            if (len(Items) > 0):
               return Items[aIdx].text.strip()

    @staticmethod
    def app_json(aVal: BeautifulSoup, aFind: dict = {'@type': 'Product'}) -> dict:
        '''
        searches value in sections <script>application/ld+json</script>
        ["app_json", [{"@type": "Product"}]]
        '''
        Items = aVal.find_all('script', type='application/ld+json')
        for x in Items:
            Data = json.loads(x.text)
            Match = FilterMatch(Data, aFind)
            if (Match == aFind):
                return Data

    @staticmethod
    def lower(aVal: str) -> str:
        '''
        string to lower case
        ["lower"]
        '''

        return aVal.lower()

    @staticmethod
    def replace(aVal: str, aFind: str, aRepl: str) -> str:
        '''
        replace string
        ["replace", ["1", "one"]]
        '''
        return aVal.replace(aFind, aRepl)

    @staticmethod
    def translate(aVal: str, aFind: str, aRepl: str, aDel: str = None) -> str:
        '''
        multiple replace string
        ["translate", ["abcd", "1234"]]
        '''
        return aVal.translate(aFind, aRepl, aDel)

    @staticmethod
    def left(aVal: str, aIdx: int) -> str:
        '''
        get left string part
        ["left", [3]]
        '''

        return aVal[:aIdx]

    @staticmethod
    def nop(aVal: object) -> object:
        '''
        no operation. for debug purpose
        ["nop"]
        '''
        return aVal

    @staticmethod
    def sub(aVal: str, aIdx: int, aEnd: int) -> str:
        '''
        get sub string
        ["sub", [2, 7]]
        '''

        return aVal[aIdx:aEnd]

    @staticmethod
    def unbracket(aVal: str, aPair: str = '()', aIdx: int = None) -> str:
        '''
        ["unbracket", ["()", -1]]
        '''

        Pattern = '\%s(.*?)\%s' % (aPair[0], aPair[1])
        Res = re.findall(Pattern, aVal)
        if (Res):
            if (aIdx is not None):
                Res = Res[aIdx].strip()
            return Res

    @staticmethod
    def concat(aVal: str, aStr: str, aRight: bool =  True) -> str:
        '''
        concatinate string to left or right side
        ["concat", ["hello", true]]
        '''

        if (aRight):
            Res = aVal + aStr
        else:
            Res = aStr + aVal
        return Res

    @staticmethod
    def print(aVal: object, aMsg: str = '') -> object:
        '''
        show value
        ["print"]
        '''

        print(aVal, aMsg)
        return aVal

    @staticmethod
    def help(aVal: object) -> list:
        '''
        show brief help
        ["help"]
        '''

        Data = GetClass(TSchemeApi)
        return [x[2] for x in Data]

