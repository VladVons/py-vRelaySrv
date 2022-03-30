'''
Author:      Vladimir Vons, Oster Inc.
Created:     2017.02.01
License:     GNU, see LICENSE for more details
Description:
'''


import sys
#
from .Util.UTime import GetDate, GetTime


class TEcho():
    # iex - Info, Error, eXception, Debug
    def __init__(self, aLevel: int = 1, aType: str = 'iexd'):
        self.Level = aLevel
        self.Type = aType

    def Write(self, aMsg: str):
        raise NotImplementedError


class TEchoConsole(TEcho):
    def Write(self, aMsg: str):
        print(aMsg)


class TEchoFile(TEcho):
    def __init__(self, aName: str):
        super().__init__()
        self.Name = aName

    def Write(self, aMsg: str):
        with open(self.Name, 'a+') as F:
            F.write(aMsg + '\n')


class TLog():
    def __init__(self):
        self.Cnt    = 0
        self.Echoes = []

        self.AddEcho(TEchoConsole())

    def AddEcho(self, aEcho: TEcho):
        Name = aEcho.__class__.__name__ 
        #List = [i for i in self.Echoes if (i.__class__.__name__ == Name)]
        List = list(filter(lambda i: (i.__class__.__name__ == Name), self.Echoes))
        if (not List):
            self.Echoes.append(aEcho) 

    def Print(self, aLevel: int, aType: str, aMsg: str, aList: tuple = '', aE: object = '') -> str:
        if (aE):
            self._DoExcept(aE)
            aEx = aE.__class__.__name__

        self.Cnt += 1
        Res = '%s,%s,%03d,%d,%s,%s,%s,%s' % (GetDate(), GetTime(), self.Cnt, aLevel, aType, aMsg, aList, aE)
        for Echo in self.Echoes:
            if (aLevel <= Echo.Level) and (aType in Echo.Type):
                Echo.Write(Res)
        return Res

    def _DoExcept(self, aE):
        sys.print_exception(aE)


Log = TLog()
