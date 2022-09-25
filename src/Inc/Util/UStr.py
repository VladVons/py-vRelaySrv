'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2020.02.21
License:     GNU, see LICENSE for more details
Description:
'''


def SplitPad(aCnt: int, aStr: str, aDelim: str) -> list:
    R = aStr.split(aDelim, aCnt - 1)
    for i in range(aCnt - len(R)):
        R.append('')
    return R

'''
class TDictRepl:
    def __init__(self, aDict: dict = {}):
        self.Dict = aDict

    def Parse(self, aStr: str) -> str:
        import re as re

        if (self.Dict):
            #r = re.compile(r'(\$\w+)\b')
            r = re.compile(r'(\$[a-zA-Z0-9]+)')
            while True:
                m = r.search(aStr)
                if (m):
                    Find = m.group(0)
                    Repl = self.Dict.get(Find, '-x-')
                    aStr = aStr.replace(Find, Repl)
                else:
                    break

        self.Dict = {}
        return aStr
'''
