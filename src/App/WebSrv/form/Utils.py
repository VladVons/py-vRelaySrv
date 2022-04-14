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
