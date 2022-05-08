'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.08
License:     GNU, see LICENSE for more details
Description:
'''


import sys
import traceback


class TPython():
    def __init__(self, aScript: str):
        self.Script = aScript
        self.ByteCode = None
        self.LineNoErr = 0

    def GetLine(self, aIdx: int) -> str:
        Lines = self.Script.splitlines()
        return Lines[aIdx]

    def Compile(self) -> bool:
        try:
            self.ByteCode = compile(self.Script, '', 'exec')
            self.LineNoErr = 0
        except (IndentationError, SyntaxError) as E:
            self.ByteCode = None
            self.LineNoErr = E.lineno
        except Exception as E:
            raise E
        return bool(self.ByteCode)

    def Exec(self, aParam: dict = {}) -> object:
        try:
            Out = {}
            Script = self.ByteCode if (self.ByteCode) else self.Script
            exec(Script, aParam, Out)
            Res = {'Data': Out.get('Res')}
            self.LineNoErr = 0
        except (IndentationError, SyntaxError) as E:
            self.LineNoErr = E.lineno
            ErrMsg = E.args[0]
        except Exception as E:
            _a, _b, tb = sys.exc_info()
            self.LineNoErr = traceback.extract_tb(tb)[-1][1]
            ErrMsg = E.args[0]

        if (self.LineNoErr):
            Res = {'Err': ErrMsg, 'LineNo': self.LineNoErr, 'Text': self.GetLine(self.LineNoErr-1)}
        return Res
