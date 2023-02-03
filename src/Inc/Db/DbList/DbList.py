# Created: 2022.03.24
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import json
import random
#
from .BeeTree import TBeeTree
from .DbCond import TDbCond
from .DbErr import TDbListException
from .DbFields import TDbFields
from .DbRec import TDbRec


class TDbList():
    def __init__(self, aFields: list = None, aData: list = None):
        if (aFields is None):
            aFields = []

        self.Tag = 0
        self.Data = []
        self._RecNo = 0
        self.BeeTree = {}
        self.Fields = None
        self.Rec = TDbRec(self)
        self.Init(aFields, aData)
        self.OptSafe = True
        self.OptSafeConvert = True
        self.OptReprLen = 25

    def __len__(self):
        return self.GetSize()

    def __iter__(self):
        self._RecNo = -1
        return self

    def __next__(self):
        if (self._RecNo >= self.GetSize() - 1):
            raise StopIteration

        self._RecNo += 1
        self._RecInit()
        return self.Rec

    def __repr__(self):
        return self._Repr()

    def _GetMaxLen(self) -> list:
        Res = [
            len(self.Fields.IdxOrd[i][0])
            for i in range(len(self.Fields))
        ]

        for Row in self.Data:
            for Idx, Val in enumerate(Row):
                Res[Idx] = max(Res[Idx], len(str(Val).strip()))

        for Idx, _ in enumerate(Res):
            Res[Idx] = min(Res[Idx], self.OptReprLen)

        return Res

    def _Repr(self):
        FieldsLen = self._GetMaxLen()
        Fields = self.Fields.GetList()

        Format = []
        for Idx, (_Key, Value) in enumerate(self.Fields.items()):
            Align = '' if Value[1] in [int, float] else '-'
            Format.append('%' + Align + str(FieldsLen[Idx]) + 's\t')
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

    def _DbExp(self, aData: list, aFields: list[str], aFieldsNew: list[list] = None) -> 'TDbList':
        Res = TDbList()
        Res.Fields = self.Fields.GetFields(aFields)
        if (aFieldsNew):
            Res.Fields.AddList(aFieldsNew)
        Res.Data = aData
        return Res

    def _RecInit(self):
        if (not self.IsEmpty()):
            self.Rec.SetData(self.Data[self._RecNo])

    def _Group(self, aFieldsUniq: list[str], aFieldsSum: list[str]) -> dict:
        Res = {}

        FieldsNoUniq = [self.Fields.GetNo(x) for x in aFieldsUniq]
        FieldsNoSum = [self.Fields.GetNo(x) for x in aFieldsSum]

        for Row in self.Data:
            FKey = tuple(Row[x] for x in FieldsNoUniq)
            if (FKey not in Res):
                Res[FKey] = []
            FSum = [Row[x] for x in FieldsNoSum]
            Res[FKey].append(FSum)
        return Res

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

    def Init(self, aFields: list, aData: list = None):
        self.Fields = TDbFields()
        self.Fields.AddList(aFields)
        self.SetData(aData)

    def InitList(self, aField: tuple, aData: list):
        self.Fields = TDbFields()
        self.Fields.Add(*aField)
        self.ImportList(aField[0], aData)

    def GetSize(self) -> int:
        return len(self.Data)

    def IsEmpty(self) -> bool:
        return (self.GetSize() == 0)

    def Empty(self):
        self.Data = []
        self._RecNo = 0

    def ExportPair(self, aFieldKey: str, aFieldVal: str) -> dict:
        '''
        Returns two binded fields as key:val
        '''
        KeyNo = self.Fields.GetNo(aFieldKey)
        ValNo = self.Fields.GetNo(aFieldVal)
        return {x[KeyNo]: x[ValNo] for x in self.Data}

    def ExportDict(self) -> list:
        return [Rec.GetAsDict() for Rec in self]

    def ExportList(self, aField: str, aUniq = False) -> list:
        '''
        Returns one field as list
        '''
        FieldNo = self.Fields.GetNo(aField)
        Res = [x[FieldNo] for x in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def ExportData(self, aFields: list = None, aCond: TDbCond = None, aRecNo: tuple = None) -> list:
        if (aFields is None):
            aFields = []
        if (aRecNo is None):
            aRecNo = (0, -1)

        Start, Finish = aRecNo
        if (Finish == -1):
            Finish = self.GetSize()

        if (aFields):
            FieldsNo = [self.Fields.GetNo(x) for x in aFields]
        else:
            aFields = self.Fields.GetList()
            FieldsNo = list(range(len(self.Fields)))

        if (aCond):
            Data = [[Val[i] for i in FieldsNo] for Val in self.Data[Start:Finish] if aCond.Find(Val)]
        else:
            #return [list(map(i.__getitem__, FieldsNo)) for i in self.Data[Start:Finish]]
            Data = [[Val[i] for i in FieldsNo] for Val in self.Data[Start:Finish]]
        return Data

    def Export(self, aWithType: bool = True) -> dict:
        '''
        Returns all data in a simple dict for future import
        '''
        return {'Data': self.Data, 'Head': self.Fields.Export(aWithType), 'Tag': self.Tag}

    def ImportAutoFields(self, aData: list, aFields: list[str]) -> 'TDbList':
        if (not aData):
            raise TDbListException('Cant auto import empty data')

        self.Data = aData
        self.Fields.AddAuto(aFields, aData[0])
        return self

    def ImportList(self, aField: str, aData: list):
        Rec = TDbRec(self)
        Rec.Init()
        FieldNo = self.Fields.GetNo(aField)
        for Row in aData:
            Arr = Rec.copy()
            Arr[FieldNo] = Row
            self.Data.append(Arr)

    def ImportDbl(self, aDbl: 'TDbList', aFields: list = None, aCond: TDbCond = None, aRecNo: tuple = (0, -1)) -> 'TDbList':
        if (aFields is None):
            aFields = []

        self.Data = aDbl.ExportData(aFields, aCond, aRecNo)
        self.Fields = aDbl.Fields.GetFields(aFields)
        self.Tag = aDbl.Tag
        return self

    def ImportPair(self, aData: dict, aKeyName: str, aFieldValue: tuple) -> 'TDbList':
        self.Fields = TDbFields([(aKeyName, str), aFieldValue])
        self.Data = [[Key, Val] for Key, Val in aData.items()]
        return self

    def Import(self, aData: dict, aWithType: bool = True) -> 'TDbList':
        self.Tag = aData.get('Tag')
        Head = aData.get('Head')
        self.Fields = TDbFields()

        if (aWithType):
            self.Data = aData.get('Data', [])
            self.Fields.Import(Head)
        else:
            self.ImportAutoFields(aData.get('Data'), Head)
        self.RecNo = 0
        return self

    def SetData(self, aData: list):
        if (aData):
            if (len(aData[0]) != len(self.Fields)):
                raise TDbListException('fields count mismatch %s and %s' % (len(aData[0]), len(self.Fields)))

            if (self.OptSafe):
                for x in aData:
                    self.RecAdd(x)
            else:
                self.Data = aData
            self.RecNo = 0
        else:
            self.Empty()

    def GetDiff(self, aField: str, aList: list) -> tuple:
        Set1 = set(self.ExportList(aField))
        Set2 = set(aList)
        return (Set1 - Set2, Set2 - Set1)

    def Find(self, aCond: TDbCond) -> int:
        for i in range(self._RecNo, self.GetSize()):
            if (aCond.Find(self.Data[i])):
                return i
        return -1

    def FindField(self, aName: str, aValue) -> int:
        FieldNo = self.Fields.GetNo(aName)
        for i in range(self._RecNo, self.GetSize()):
            if (self.Data[i][FieldNo] == aValue):
                return i
        return -1

    def Search(self, aField: str, aVal) -> int:
        if (not aField in self.BeeTree):
            raise TDbListException('SearchAdd()')
        return self.BeeTree[aField].Search(aVal)

    def SearchAdd(self, aField: str, aAllowEmpty: bool = False) -> TBeeTree:
        BeeTree = TBeeTree()
        FieldNo = self.Fields.GetNo(aField)
        for RowNo, Row in enumerate(self.Data):
            Data = Row[FieldNo]
            if (Data or aAllowEmpty):
                BeeTree.Add((Data, RowNo))
        self.BeeTree[aField] = BeeTree
        return BeeTree

    def AddField(self, aFields: list = None):
        if (aFields is None):
            aFields = []

        self.Fields.AddList(aFields)
        for Row in self.Data:
            for Field in aFields:
                Def = self.Fields[Field[0]][2]
                Row.append(Def)

    def DelField(self, aField: str):
        FieldNo = self.Fields.GetNo(aField)
        for Row in self.Data:
            del Row[FieldNo]

        Fields = self.Fields.GetList()
        Fields.remove(aField)
        self.Fields = self.Fields.GetFields(Fields)

    def Clone(self, aFields: list[str] = None, aCond: TDbCond = None, aRecNo: tuple = None) -> 'TDbList':
        if (aFields is None):
            aFields = []
        if (aRecNo is None):
            aRecNo = (0, -1)

        Data = self.ExportData(aFields, aCond, aRecNo)
        return self._DbExp(Data, aFields)

    def Group(self, aFieldsUniq: list[str], aFieldsSum: list[str] = None) -> 'TDbList':
        if (aFieldsSum is None):
            aFieldsSum = []

        Grouped = self._Group(aFieldsUniq, aFieldsSum)
        Data = []
        for Key, Val in Grouped.items():
            ZipVal = zip(*Val)
            Row = list(Key) + [sum(i) for i in ZipVal] + [len(Val)]
            Data.append(Row)

        # FieldsSum = [(Key + '_Sum', Val[1]) for Key, Val in self.Fields.GetFields(aFieldsSum).items()]
        # return self._DbExp(Data, aFieldsUniq, FieldsSum + [('Count', int)])
        return self._DbExp(Data, aFieldsUniq + aFieldsSum, [('Count', int)])

    def New(self) -> 'TDbList':
        return self._DbExp([], [])

    def Sort(self, aFields: list[str], aReverse: bool = False) -> 'TDbList':
        if (len(aFields) == 1):
            FieldNo = self.Fields.GetNo(aFields[0])
            self.Data.sort(key=lambda x: (x[FieldNo]), reverse=aReverse)
        else:
            F = ''
            for Field in aFields:
                F += 'x[%s],' % self.Fields.GetNo(Field)
            Script = 'self.Data.sort(key=lambda x: (%s), reverse=%s)' % (F, aReverse)
            # pylint: disable-next=eval-used
            eval(Script)
        self.RecNo = 0
        return self

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecNo = 0

    def RecGo(self, aNo: int) -> TDbRec:
        self.RecNo = aNo
        return self.Rec

    def RecAdd(self, aData: list = None) -> TDbRec:
        if (aData):
            self.Rec.SetData(aData)
        else:
            self.Rec.Init()
        self.Data.append(self.Rec.copy())
        self._RecNo = self.GetSize() - 1
        return self.Rec

    def RecPop(self, aRecNo: int = -1) -> TDbRec:
        Res = TDbRec(self)
        Res.SetData(self.Data.pop(aRecNo))
        return Res

    def Save(self, aFile: str, aFormat: bool = False):
        with open(aFile, 'w', encoding = 'utf-8') as F:
            if (aFormat):
                json.dump(self.Export(), F, indent=2, sort_keys=True, ensure_ascii=False)
            else:
                json.dump(self.Export(), F)

    def Load(self, aFile: str) -> 'TDbList':
        with open(aFile, 'r', encoding = 'utf-8') as F:
            Data = json.load(F)
            self.Import(Data)
            return self


if (__name__ == '__main__'):
    pass
