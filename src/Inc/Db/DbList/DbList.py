# Created: 2023.02.05
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

from .DbBase import TDbBase
from .DbCond import TDbCond
from .DbRec import TDbRec


class TDbList(TDbBase):
    def __init__(self, aFields: list[str] = None, aData: list = None):
        super().__init__()
        self.Rec = TDbRec()

        if (aFields):
            self.Init(aFields, aData)

    def _DbExp(self, aData: list, aFields: list[str], aFieldsNew: list[list] = None) -> 'TDbList':
        Res = self.__class__()
        if (aFieldsNew):
            aFields += aFieldsNew
        Res.Init(aFields, aData)
        return Res

    def _GetFieldNo(self, aField: str) -> int:
        return self.Rec.Fields.get(aField)

    def _GetFields(self) -> list[str]:
        return self.Rec.Fields.keys()

    def _RecInit(self) -> TDbRec:
        self.Rec.Data = self.Data[self._RecNo]
        return self.Rec

    def AddField(self, aFields: list[str]):
        for i, x in enumerate(aFields, len(self.Rec.Fields)):
            self.Rec.Fields[x] = i

        Len = len(aFields)
        for x in self.Data:
            x += [None] * Len

    def Export(self) -> dict:
        '''
        Returns all data in a simple dict for future import
        '''
        return {'Data': self.Data, 'Head': self.Rec.Fields.keys(), 'Tag': self.Tag}

    def Import(self, aData: dict) -> 'TDbList':
        self.Tag = aData.get('Tag')
        return self.Init(aData.get('Head'), aData.get('Data'))

    def ImportDbl(self, aDbl: 'TDbList', aFields: list = None, aCond: TDbCond = None, aRecNo: tuple = (0, -1)) -> 'TDbList':
        if (aFields is None):
            # pylint: disable-next=protected-access
            aFields = aDbl._GetFields()

        self.Init(aFields, aDbl.ExportData(aFields, aCond, aRecNo))
        return self

    def Init(self, aFields: list[str], aData: list) -> 'TDbList':
        self.Rec.Fields = {x: i for i, x in enumerate(aFields)}
        self.Data = aData
        if (aData):
            self._RecInit()
        else:
            self.Rec.Data = []
        return self

    def InitList(self, aField: str, aData: list) -> 'TDbList':
        Data = [[x] for x in aData]
        return self.Init([aField], Data)

    def RecAdd(self, aData: list = None) -> list:
        if (aData):
            self.Data.append(aData.copy())
        else:
            Data = [None] * len(self.Rec.Fields)
            self.Data.append(Data)
        self._RecNo = self.GetSize() - 1
        return self._RecInit()

    def RecGo(self, aNo: int) -> TDbRec:
        self.RecNo = aNo
        return self.Rec

    def RecPop(self, aRecNo: int = -1) -> TDbRec:
        Res = TDbRec()
        Res.Fields = self.Rec.Fields
        Res.Data = self.Data.pop(aRecNo)
        return Res
