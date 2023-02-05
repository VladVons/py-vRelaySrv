# Created: 2023.02.05
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import random
import json
#
from .BeeTree import TBeeTree
from .DbCond import TDbCond
from .DbErr import TDbListException


class TDbBase():
    def __init__(self):
        self.Data = []
        self.Tag = 0
        self._RecNo = 0
        self.BeeTree = {}
        self.OptReprLen = 25

    @property
    def RecNo(self):
        return self._RecNo

    @RecNo.setter
    def RecNo(self, aNo: int):
        if (self.IsEmpty()):
            self._RecNo = 0
        else:
            if (aNo < 0):
                aNo = self.GetSize() + aNo
            self._RecNo = min(aNo, self.GetSize() - 1)
        self._RecInit()

    def __len__(self):
        return self.GetSize()

    def __iter__(self):
        self._RecNo = -1
        return self

    def __next__(self):
        if (self._RecNo >= self.GetSize() - 1):
            raise StopIteration

        self._RecNo += 1
        return self._RecInit()

    def __repr__(self):
        return self._Repr()

    def _RecInit(self):
        raise NotImplementedError()

    def _GetFieldNo(self, aField: str) -> int:
        raise NotImplementedError()

    def _GetFields(self) -> list[str]:
        raise NotImplementedError()

    def _Repr(self):
        def _GetMaxLen() -> list:
            nonlocal Fields

            Res = [len(x) for x in Fields]

            for Row in self.Data:
                for Idx, Val in enumerate(Row):
                    Res[Idx] = max(Res[Idx], len(str(Val).strip()))

            for Idx, _ in enumerate(Res):
                Res[Idx] = min(Res[Idx], self.OptReprLen)

            return Res

        Fields = self._GetFields()
        FieldsLen = _GetMaxLen()

        if (self.Data):
            Format = []
            for Idx, x in enumerate(self.Data[0]):
                Align = '' if x in [int, float] else '-'
                Format.append('%' + Align + str(FieldsLen[Idx]) + 's\t')
        else:
            Format = [f'%{x}s\t' for x in FieldsLen]
        Format = ''.join(Format)

        Res = []
        Res.append(Format % tuple(Fields))
        for Idx, Row in enumerate(self.Data):
            Trimmed = []
            for x in Row:
                x = str(x)
                if (len(x) > self.OptReprLen):
                    x = x[:self.OptReprLen - 3] + '...'
                Trimmed.append(x)
            Res.append(Format % tuple(Trimmed))
        Res.append(f'records: {self.GetSize()}')
        return '\n'.join(Res)

    def _Group(self, aFieldsUniq: list[str], aFieldsSum: list[str]) -> dict:
        Res = {}

        FieldsNoUniq = [self._GetFieldNo(x) for x in aFieldsUniq]
        FieldsNoSum = [self._GetFieldNo(x) for x in aFieldsSum]

        for Row in self.Data:
            FKey = tuple(Row[x] for x in FieldsNoUniq)
            if (FKey not in Res):
                Res[FKey] = []
            FSum = [Row[x] for x in FieldsNoSum]
            Res[FKey].append(FSum)
        return Res

    def DelField(self, aField: str) -> list[str]:
        FieldNo = self._GetFieldNo(aField)
        for Row in self.Data:
            del Row[FieldNo]

        Fields = self._GetFields()
        Fields.remove(aField)
        return Fields

    def GetSize(self) -> int:
        return len(self.Data)

    def IsEmpty(self) -> bool:
        return (self.GetSize() == 0)

    def Empty(self):
        self.Data = []
        self._RecNo = 0

    def Import(self, aData: dict) -> 'TDbBase':
        raise NotImplementedError()

    def Export(self) -> dict:
        raise NotImplementedError()

    def GetDiff(self, aField: str, aList: list) -> tuple:
        Set1 = set(self.ExportList(aField))
        Set2 = set(aList)
        return (Set1 - Set2, Set2 - Set1)

    def ExportList(self, aField: str, aUniq = False) -> list:
        '''
        Returns one field as list
        '''
        FieldNo = self._GetFieldNo(aField)
        Res = [x[FieldNo] for x in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def ExportPair(self, aFieldKey: str, aFieldVal: str) -> dict:
        '''
        Returns two binded fields as key:val
        '''
        KeyNo = self._GetFieldNo(aFieldKey)
        ValNo = self._GetFieldNo(aFieldVal)
        return {x[KeyNo]: x[ValNo] for x in self.Data}

    def FindField(self, aName: str, aValue) -> int:
        FieldNo = self._GetFieldNo(aName)
        for i in range(self._RecNo, self.GetSize()):
            if (self.Data[i][FieldNo] == aValue):
                return i
        return -1

    def Find(self, aCond: TDbCond) -> int:
        for i in range(self._RecNo, self.GetSize()):
            if (aCond.Find(self.Data[i])):
                return i
        return -1

    def Load(self, aFile: str) -> 'TDbData':
        with open(aFile, 'r', encoding = 'utf-8') as F:
            Data = json.load(F)
            self.Import(Data)
            return self

    def Save(self, aFile: str, aFormat: bool = False):
        with open(aFile, 'w', encoding = 'utf-8') as F:
            if (aFormat):
                json.dump(self.Export(), F, indent=2, sort_keys=True, ensure_ascii=False)
            else:
                json.dump(self.Export(), F)

    def Search(self, aField: str, aVal) -> int:
        if (not aField in self.BeeTree):
            raise TDbListException('SearchAdd()')
        return self.BeeTree[aField].Search(aVal)

    def SearchAdd(self, aField: str, aAllowEmpty: bool = False) -> TBeeTree:
        BeeTree = TBeeTree()
        FieldNo = self._GetFieldNo(aField)
        for RowNo, Row in enumerate(self.Data):
            Data = Row[FieldNo]
            if (Data or aAllowEmpty):
                BeeTree.Add((Data, RowNo))
        self.BeeTree[aField] = BeeTree
        return BeeTree

    def Sort(self, aFields: list[str], aReverse: bool = False) -> 'TDbBase':
        if (len(aFields) == 1):
            FieldNo = self._GetFieldNo(aFields[0])
            self.Data.sort(key=lambda x: (x[FieldNo]), reverse=aReverse)
        else:
            F = ''
            for Field in aFields:
                F += 'x[%s],' % self._GetFieldNo(Field)
            Script = 'self.Data.sort(key=lambda x: (%s), reverse=%s)' % (F, aReverse)
            # pylint: disable-next=eval-used
            eval(Script)
        self.RecNo = 0
        return self

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecNo = 0
