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
    def Write(self, aMsg: str):
        pass


class TEchoConsole(TEcho):
    def Write(self, aMsg: str):
        print(aMsg)


class TEchoFile(TEcho):
    def __init__(self, aName: str):
        self.Name = aName

    def Write(self, aMsg: str):
        with open(self.Name, 'a+') as F:
            F.write(aMsg + '\n')


class TLog():
    def __init__(self):
        self.Level  = 1
        self.Cnt    = 0
        self.Echoes = []

        self.AddEcho(TEchoConsole())

    def AddEcho(self, aEcho: TEcho):
        self.Echoes.append(aEcho) 

    def Print(self, aLevel: int, aType: str, *aParam) -> str:
        R = '' 
        if (aLevel <= self.Level):
            self.Cnt += 1
            R = '%s,%s,%03d,%d,%s,%s%s' % (GetDate(), GetTime(), self.Cnt, aLevel, aType, ' ' * aLevel, list(aParam))
            if (aType == 'x') and (len(aParam) > 1):
                self._DoExcept(aParam[1])

            for Echo in self.Echoes:
                Echo.Write(R)
        return R

    def _DoExcept(self, aE):
        sys.print_exception(aE)


Log = TLog()
