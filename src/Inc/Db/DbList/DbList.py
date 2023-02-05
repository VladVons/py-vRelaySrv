# Created: 2022.03.24
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from .DbBase import TDbBase
from .DbCond import TDbCond
from .DbErr import TDbListException
from .DbFields import TDbFields
from .DbRec import TDbRec


class TDbList(TDbBase):
    def __init__(self, aFields: list = None, aData: list = None):
        super().__init__()

        self.Fields = None
        if (aFields is None):
            aFields = []

        self.OptSafe = True
        self.OptSafeConvert = True

        self.Rec = TDbRec(self)
        self.Init(aFields, aData)

    def _GetFieldNo(self, aField: str) -> int:
        return self.Fields.GetNo(aField)

    def _GetFields(self) -> list[str]:
        return self.Fields.keys()

    def _DbExp(self, aData: list, aFields: list[str], aFieldsNew: list[list] = None) -> 'TDbList':
        Res = TDbList()
        Res.Fields = self.Fields.GetFields(aFields)
        if (aFieldsNew):
            Res.Fields.AddList(aFieldsNew)
        Res.Data = aData
        return Res

    def _RecInit(self) -> TDbRec:
        if (not self.IsEmpty()):
            self.Rec.SetData(self.Data[self._RecNo])
        return self.Rec

    def Init(self, aFields: list, aData: list = None):
        self.Fields = TDbFields()
        self.Fields.AddList(aFields)
        self.SetData(aData)

    def InitList(self, aField: tuple, aData: list):
        self.Fields = TDbFields()
        self.Fields.Add(*aField)
        self.ImportList(aField[0], aData)

    def ExportDict(self) -> list:
        return [Rec.GetAsDict() for Rec in self]

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

    def Export(self) -> dict:
        '''
        Returns all data in a simple dict for future import
        '''
        return {'Data': self.Data, 'Head': self.Fields.Export(), 'Tag': self.Tag}

    def ImportAutoFields(self, aData: list, aFields: list[str]) -> 'TDbList':
        if (not aData):
            raise TDbListException('Cant auto import empty data')

        self.Data = aData
        self.Fields.AddAuto(aFields, aData[0])
        self.RecNo = 0
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

    def Import(self, aData: dict) -> 'TDbList':
        self.Tag = aData.get('Tag')
        self.Fields = TDbFields()
        self.Data = aData.get('Data', [])
        self.Fields.Import(aData.get('Head'))
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

    def AddField(self, aFields: list = None):
        if (aFields is None):
            aFields = []

        self.Fields.AddList(aFields)
        for Row in self.Data:
            for Field in aFields:
                Def = self.Fields[Field[0]][2]
                Row.append(Def)

    def DelField(self, aField: str):
        Fields = super().DelField(aField)
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
