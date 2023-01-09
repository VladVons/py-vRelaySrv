import os
import json
#
from Inc.Util.Obj import DeepGet
from Inc.UtilP.FS import GetFiles


class TDbModel():
    def __init__(self, aDir: str):
        self.Dir = aDir
        self.Tables = []

        self.Data = {}
        self.Refers = {}
        self._InitData()

    def _GetDirs(self):
        return list(GetFiles(self.Dir, '.*', 'd', 1))

    def _InitData(self):
        for Dir in self._GetDirs():
            Name = os.path.basename(Dir)
            File = f'{Dir}/Meta.json'
            with open(File, 'r', encoding='UTF8') as F:
                self.Data[Name] = json.load(F)
                for TableK, TableD in self.Data[Name].get('table', {}).items():
                    for _ForeignK, ForeignD in TableD.get('foreign_key', {}).items():
                        TebleRef = ForeignD.get('table')
                        self.Refers[TebleRef] = self.Refers.get(TebleRef, []) + [TableK]

    def _FindTable(self, aName: str) -> tuple:
        for Key, Val in self.Data.items():
            Res = DeepGet(Val, f'table.{aName}')
            if (Res):
                return (Key, Res)

    def _LoadTable(self, aName: str):
        if (aName in self.Tables):
            return

        Table = self._FindTable(aName)
        if (Table):
            self.Tables.append(aName)

            ForeignKey = Table[1].get('foreign_key', {})
            for _ForeignK, ForeignD in ForeignKey.items():
                ForeignTable = ForeignD['table']
                self._LoadTable(ForeignTable)
                for RefersD in self.Refers.get(ForeignTable, []):
                    self._LoadTable(RefersD)
        else:
            print(f' Table not found {aName}')

    def LoadModel(self, aName: str):
        Tables = DeepGet(self.Data, f'{aName}.table', {})
        for Table in Tables:
            self._LoadTable(Table)
