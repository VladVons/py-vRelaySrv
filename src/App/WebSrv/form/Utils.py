'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.04.11
License:     GNU, see LICENSE for more details
Description:
'''


import json


class TJsonEncoder(json.JSONEncoder):
    def default(self, aObj):
        As = str(aObj)
        return As

def GetLeadCharCnt(aValue: str, aChar: str) -> int:
    return len(aValue) - len(aValue.lstrip(aChar))

def FormatScript(aScript: str) -> str:
    Res = []
    Lines = aScript.splitlines()
    PadSpaces = GetLeadCharCnt(Lines[1], ' ')
    for Line in Lines:
        if (Line.strip()):
            if (Line.startswith(' ')):
                Line = Line[PadSpaces:]
            else:
                Spaces = GetLeadCharCnt(Res[-1], ' ')
                Line = (' ' * Spaces) + Line
            Res.append(Line)
    return '\n'.join(Res)
