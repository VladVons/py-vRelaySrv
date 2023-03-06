# Created: 2023.03.05
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import json
#
from Inc.Sql import TDbPg, TDbExecPool


class TLoaderLang(dict):
    async def Add(self, aPath: str) -> dict:
        raise NotImplementedError()

    def Get(self, aKey: str) -> str:
        return self.get(aKey, f'-{aKey}-')


class TLoaderLangFs(TLoaderLang):
    def __init__(self, aLang: str, aDirRoot: str):
        self.Dir = f'{aDirRoot}/{aLang}'

    async def Add(self, aPath: str):
        File = f'{self.Dir}/{aPath}.json'
        with open(File, 'r', encoding = 'utf8') as F:
            Data = json.load(F)
        self.update(Data)


class TLoaderQueryDb(TLoaderLang):
    def __init__(self, aLang: int, aDb: TDbPg):
        self.Lang = aLang
        self.Db = aDb

    async def Add(self, aPath: str):
        pass
