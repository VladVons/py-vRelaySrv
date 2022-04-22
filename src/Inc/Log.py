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
        self.Fmt = ['d', 't', 'c', 'aL', 'aT', 'aM', 'aD', 'aE']

    def _Format(self, aArgs: dict) -> str:
        #Arr = [x + ':' +str(aArgs.get(x, '')) for x in self.Fmt]
        Arr = [str(aArgs.get(x, '')) for x in self.Fmt]
        return ', '.join(Arr)

    def _Write(self, aMsg: str):
        raise NotImplementedError

    def Write(self, aArgs: dict):
        if (aArgs.get('aL') <= self.Level) and (aArgs.get('aT') in self.Type):
            Msg = self._Format(aArgs)
            self._Write(Msg)


class TEchoConsole(TEcho):
    def _Write(self, aMsg: str):
        print(aMsg)


class TEchoFile(TEcho):
    def __init__(self, aName: str):
        super().__init__()
        self.Name = aName

    def _Write(self, aMsg: str):
        with open(self.Name, 'a+') as F:
            F.write(aMsg + '\n')


class TLog():
    def __init__(self):
        self.Cnt    = 0
        self.Echoes = []

        self.AddEcho(TEchoConsole())

    def FindEcho(self, aClassName: str) -> list:
        #return list(filter(lambda i: (i.__class__.__name__ == aClassName), self.Echoes))
        return [i for i in self.Echoes if (i.__class__.__name__ == aClassName)]

    def AddEcho(self, aEcho: TEcho):
        Name = aEcho.__class__.__name__
        if (not self.FindEcho(Name)):
            self.Echoes.append(aEcho)

    def Print(self, aLevel: int, aType: str, aMsg: str, aData: list = [], aE: Exception = None) -> str:
        if (aE):
            aData.append(aE.__class__.__name__)
            EMsg = self._DoExcept(aE)
            if (EMsg):
                aData.append(EMsg)

        self.Cnt += 1
        Args = {'aL': aLevel, 'aT': aType, 'aM': aMsg, 'aD': aData, 'aE': aE, 'c': self.Cnt, 'd': GetDate(), 't': GetTime()}
        for Echo in self.Echoes:
            Echo.Write(Args)

    def _DoExcept(self, aE):
        sys.print_exception(aE)


Log = TLog()
