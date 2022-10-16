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
from Inc.Util.UObj import GetNestedKey
from IncP.Utils import FilterMatch
from IncP.ImportInf import GetClass


_Whitespace = ' \t\n\r\v\f\xA0✓→'
_Digits = '0123456789'
_DigitsDot = _Digits + '.'
_DigitsDotComma = _Digits + '.,'
#_XlatEntitles = [('&nbsp;', ' '), ('&lt;', '<'), ('&amp;', '&'), ('&quot;', '"'), ('&apos;', "'")]
#
#ReCmp_Strip = re.compile(r'^\s+|\s+$')
ReCmp_Serial = re.compile(r'[A-Z0-9\-/]{5,}')


class TInStock():
    _MatchYes = [
        # en
        'http://schema.org/instock',
        'https://schema.org/instock',
        'instock',

        # ua
        'в наявності на складі',
        'в наявності',
        'в кошик',
        'до кошика',
        'додати у кошик',
        'добавити в корзину',
        'є в наявності',
        'є на складі',
        'закінчується',
        'купити',
        'на складі',
        'товар в наявності',
        'товар є в наявності',
        'склад',

        # ru
        'в корзину',
        'в наличии на складе',
        'в наличии',
        'добавить в корзину',
        'есть в наличии',
        'есть на складе',
        'есть',
        'заканчивается',
        'купить',
        'на складе',
        'товар в наличии',
        'товар есть в наличии',
    ]

    _MatchNo = [
        # ua
        'немає в наявності',

        # ru
        'нет в наличии'
    ]

    _Del = [
        ' шт.'
    ]

    def __init__(self):
        self.Trans = str.maketrans('', '', _Digits)

    def Check(self, aVal: str, aMatch: bool) -> bool:
        aVal = aVal.translate(self.Trans).strip().lower()
        for Item in self._Del:
            aVal = aVal.replace(Item, '')
        Match = self._MatchYes if (aMatch) else self._MatchNo
        return aVal in Match

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

        if (After == '') and (x in _DigitsDotComma):
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


class TSchemeExt():
    def __init__(self, aParent):
        self.Parent = aParent

    def url_pad(self, aVal: str) -> str:
        '''
        pad url with host prefix
        ["url_pad"]
        '''

        if (not aVal.startswith('http')):
            aVal = self.Parent.Var.get('$host') + '/' + aVal.strip('/')
        return aVal

    def var_get(self, _aNotUsed: object, aName: str) -> object:
        '''
        get variable
        ["var_get", ["$root"]]
        '''

        Res = self.Parent.Var.get(aName)
        if (not Res):
            self.Parent.Err.append('%s (unknown)' % (aName))
        return Res

    def var_set(self, aVal: object, aName: str) -> object:
        '''
        set current chain value to variable
        ["var_set", ["$Price"]]
        '''

        self.Parent.Var[aName] = aVal
        return aVal


class TSchemeApi():
    def __new__(cls):
        raise TypeError('Cant instantiate static class')

    @staticmethod
    def _text(aVal: BeautifulSoup) -> str:
        '''
        equal to text + strip
        ["text"]
        '''

        return TSchemeApi.strip(aVal.get_text())

    @staticmethod
    def strip(aVal: str) -> str:
        '''
        remove invisible chars
        ["strip"]
        '''

        #return aVal.strip()
        return aVal.strip(_Whitespace)
        #return ReCmp_Strip.sub('', aVal)

    @staticmethod
    def _strip_all(aVal: str) -> str:
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
    def _length(aVal: object) -> int:
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
    def list_sort(aVal: list, aReverse: bool = False) -> list:
        '''
        sort list alphabetically
        ["list_sort", [False]]
        '''

        if (isinstance(aVal, list)):
            return sorted(aVal, reverse=aReverse)

    @staticmethod
    def list_sort_len(aVal: list, aReverse: bool = False) -> list:
        '''
        sort string list by length
        ["list_sort_len", [False]]
        '''

        if (isinstance(aVal, list)):
            return sorted(aVal, key=len, reverse=aReverse)

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

        if (not After) and (Before):
            After = Before

        return (float(Dig), After.lower())

    @staticmethod
    def price_find(aVal: str, aCur: str = 'грн') -> list:
        '''
        get prices from string using regEx r'[\d\.]{2,}\s*' + aCur
        ["price_find"]
        '''

        Pattern = r'[\d\.]{2,}\s*' + aCur
        Res = re.findall(Pattern, aVal)
        if (Res):
            return Res

    @staticmethod
    def stock(aVal: str, aPresent: bool = True) -> bool:
        '''
        Get stock availability
        ["stock"]
        '''

        return InStock.Check(aVal, aPresent) == aPresent

    @staticmethod
    def serial_check(aVal: str, aLen: int = 5) -> str:
        '''
        check ranges [A..Z], [0..9], [-/ ] and length >= aLen
        ["serial_check"]
        '''

        if (len(aVal) >= aLen):
            Res = [x for x in aVal if ('A' <= x <= 'Z') or (x in '0123456789-/. ')]
            if (len(aVal) == len(Res)):
                return aVal

    @staticmethod
    def serial_find(aVal: str, aMatch: str = r'[A-Z0-9\-\./]{5,}') -> str:
        '''
        get serial number with regex matches
        ["serial_find"]
        '''

        #Res = ReCmp_Serial.findall(aVal)
        Res = re.findall(aMatch, aVal)
        if (Res):
            return Res

    @staticmethod
    def is_equal(aVal: str, aStr: list) -> bool:
        '''
        compare values
        ["is_equal", ["InStock", "available"]]
        '''

        if (isinstance(aStr, list)):
            return (aVal in aStr)

    @staticmethod
    def val2bool(aVal: object) -> bool:
        '''
        convert value to boolean
        ["val2bool"]
        '''

        return not (aVal is None)

    @staticmethod
    def not_none(aVal: list) -> object:
        '''
        get first not None item
        ["not_none"]
        '''

        for x in aVal:
            if not (x is None):
                return x

    @staticmethod
    def search(aVal: object, aStr: list) -> bool:
        '''
        search any string value from a list
        ["search", ["InStock", "available"]]
        '''

        if (isinstance(aStr, list)):
            for x in aStr:
                if (aVal.find(x) >= 0):
                    return True
            return False

    @staticmethod
    def _compare(aVal: object, aOp: str, aValue = None) -> bool:
        Func = getattr(operator, aOp, None)
        if (Func):
            if (aValue is None):
                Res = Func(aVal)
            else:
                Res = Func(aVal, aValue)
            return Res

    @staticmethod
    def _dig_lat(aVal: str) -> str:
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
    def _json2txt(aVal: dict) -> str:
        '''
        convert json to text
        ["json2txt"]
        '''

        return json.dumps(aVal, indent=2, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def gets(aVal: dict, aKeys: str) -> object:
        '''
        multiple get. equal to get('key1').get('key2')
        ["gets", ["offers.availability"]]
        '''

        return GetNestedKey(aVal, aKeys)

    @staticmethod
    def breadcrumb(aVal: BeautifulSoup, aFind: list, aIdx: int, aChain: bool = True) -> str:
        '''
        equal to find_all() + list()
        ["breadcrumb", [["a"], -1]]
        '''

        if (hasattr(aVal, 'find_all')):
            Items = aVal.find_all(*aFind)
            if (Items):
                if (aChain):
                    Items = Items if (aIdx == -1) else Items[:aIdx + 1]
                    Arr = [TSchemeApi.strip(x.text) for x in Items]
                    Arr = [x for x in Arr if (len(x) > 1)]
                    Res = '/'.join(Arr)
                else:
                    Res = Items[aIdx].text.strip()
                return Res

    @staticmethod
    def app_json(aVal: BeautifulSoup, aFind: dict = None) -> dict:
        '''
        searches value in sections <script>application/ld+json</script>
        ["app_json", [{"@type": "Product"}]]
        '''
        if (aFind is None):
            aFind = {'@type': 'Product'}

        Res = {}
        Items = aVal.find_all('script', type='application/ld+json')
        for x in Items:
            Data: str = x.text
            #Pos1 = Data.find('{')
            #Pos2 = Data.rfind('}')
            #if (Pos1 == -1) or (Pos2 == -1):
            #    continue
            #Data = Data[Pos1 : Pos2 + 1]

            try:
                Data = json.loads(Data, strict=False)
            except ValueError:
                return None

            if (isinstance(Data, list)):
                Data = Data[0]

            if (isinstance(Data, dict)):
                if (aFind):
                    Match = FilterMatch(Data, aFind)
                    if (Match == aFind):
                        return Data
                else:
                    Name = Data.get('@type')
                    Res[Name] = Data
        if (len(Res) > 0):
            return Res

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
    def _translate(aVal: str, aFind: str, aRepl: str, aDel: str = None) -> str:
        '''
        multiple replace string
        ["translate", ["abcd", "1234"]]
        '''
        return aVal.translate(aFind, aRepl, aDel)

    @staticmethod
    def _left(aVal: str, aIdx: int) -> str:
        '''
        get left string part
        ["left", [3]]
        '''

        return aVal[:aIdx]

    @staticmethod
    def comment(aVal: object, aText: str = '') -> object:
        '''
        comment
        ["comment", ["just comment"]]
        '''

        if (aText):
            print(aText)
        return aVal

    @staticmethod
    def none(_aVal: object) -> None:
        '''
        return None and stop parsing
        ["none"]
        '''

        return None

    @staticmethod
    def _sub(aVal: str, aIdx: int, aEnd: int) -> str:
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

        Pattern = r'\%s(.*?)\%s' % (aPair[0], aPair[1])
        Res = re.findall(Pattern, aVal)
        if (Res):
            if (aIdx is not None):
                Res = Res[aIdx].strip()
            return Res

    @staticmethod
    def _concat(aVal: str, aStr: str, aRight: bool =  True) -> str:
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
    def _print(aVal: object) -> object:
        '''
        show value
        ["print"]
        '''

        print(aVal)
        return aVal

    @staticmethod
    def _help(_aVal: object) -> list:
        '''
        show brief help
        ["help"]
        '''

        Data = GetClass(TSchemeApi)
        return [x[2] for x in Data]


class TSchemeApiExt():
    @staticmethod
    def ext_image(aIdx: int = 0) -> list:
        return [
            ['find_all', ['img']],
            ['list', [aIdx]],
            ['get', ['src']],
            ['url_pad']
        ]

    @staticmethod
    def ext_image_og() -> list:
        return [
            ['find', ['head']],
            ['find', ['meta', {'property': 'og:image'}]],
            ['get', ['content']],
            ['url_pad']
        ]

    @staticmethod
    def ext_category_prom(aIdx: int = -2) -> list:
        return [
            ['find', ['div', {'class': 'b-breadcrumb'}]],
            ['get', ['data-crumbs-path']],
            ['txt2json'],
            ['list', [aIdx]],
            ['get', ['name']]
        ]

    @staticmethod
    def ext_price_app(aTxt2Float: bool = False) -> list:
        txt2float = ['txt2float'] if (aTxt2Float) else ['comment']
        return [
            ['get', ['offers']],
            ['as_list', [
                [
                    ['get', ['price']],
                    txt2float
                ],
                [
                    ['get', ['priceCurrency']]
                ]
            ]]
        ]

