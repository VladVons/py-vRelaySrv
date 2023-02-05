# Created: 2023.02.05
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

from .DbBase import TDbBase


class TDbData(TDbBase):
    def __init__(self, aFields: list[str] = None, aData: list = None):
        super().__init__()

        self.Fields: dict
        self.Rec: list

        if (aFields):
            self.Init(aFields, aData)

    def _GetFieldNo(self, aField: str) -> int:
        return self.Fields.get(aField)

    def _GetFields(self) -> list[str]:
        return self.Fields.keys()

    def _RecInit(self) -> list:
        self.Rec = self.Data[self._RecNo]
        return self.Rec

    def Export(self) -> dict:
        '''
        Returns all data in a simple dict for future import
        '''
        return {'Data': self.Data, 'Head': self.Fields.keys(), 'Tag': self.Tag}

    def GetField(self, aField: str, aDef = None) -> object:
        Res = self.Rec[self._GetFieldNo(aField)]
        if (Res is None):
            Res = aDef
        return Res

    def Import(self, aData: dict) -> 'TDbData':
        self.Tag = aData.get('Tag')
        return self.Init(aData.get('Head'), aData.get('Data'))

    def Init(self, aFields: list[str], aData: list) -> 'TDbData':
        self.Fields = {x: i for i, x in enumerate (aFields)}
        self.Data = aData
        if (aData):
            self._RecInit()
        else:
            self.Rec = []
        return self

    def RecAdd(self, aData: list = None) -> list:
        if (aData):
            self.Data.append(aData.copy())
        else:
            Data = [None] * len(self.Fields)
            self.Data.append(Data)
        self._RecNo = self.GetSize() - 1
        return self._RecInit()

    def SetField(self, aField: str, aData):
        self.Rec[self.Fields[aField]] = aData
