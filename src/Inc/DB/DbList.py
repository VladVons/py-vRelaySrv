'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.24
License:     GNU, see LICENSE for more details

    Dbl1 = TDbList( [('User', str), ('Age', int), ('Male', bool, True)] )
    Data = [['User2', 22, True], ['User1', 11, False], ['User3', 33, True]]
    Dbl1.Safe = True
    Dbl1.SetData(Data)

    Dbl1.AddField([('Weight', int, 100)])

    Rec = Dbl1.RecAdd()
    Rec.SetField('User', 'User4')
    Rec.SetField('Age', 20)
    Rec.SetField('Male', False)
    Rec.Flush()

    Dbl1.Data.append(['User5', 30, False])
    Dbl1.RecAdd(['User6', 40, True])
    Dbl1.Rec.Flush()

    Dbl1.RecAdd()
    Dbl1.Rec.SetAsDict({'User': 'User7', 'Age': 45, 'Male': True})
    Dbl1.Rec.Flush()

    Dbl1.RecNo = 0
    print()
    print('GetSize:', Dbl1.GetSize())
    print('Data:', Dbl1.Data)
    print('Rec:', Dbl1.Rec)
    print('Rec.GetAsDict:', Dbl1.Rec.GetAsDict())
    print('Rec.GetAsTuple:', Dbl1.Rec.GetAsTuple())
    print('Rec.GetList:', Dbl1.ExportList('User', True))

    Dbl1.Sort(['User', 'Age'], True)
    for Idx, Rec in enumerate(Dbl1):
        print(Idx, Rec.GetField('User'),  Rec[1])

    print()
    Db3 = Dbl1.Clone(aFields = ['User', 'Age'], aRecNo = (0, 3))
    Db3.Shuffle()
    for Idx, Rec in enumerate(Db3):
        print(Idx, Rec.GetField('User'),  Rec[1])

    Db3.self.RecNo = -2
    print('Db3.Rec', Db3.Rec)

    print()
    Cond = TDbCond().AddFields([
        ['lt', (Dbl1, 'Age'), 40, True],
        ['eq', (Dbl1, 'Male'), True, True]
    ])
    Dbl2 = Dbl1.Clone(aCond=Cond)
    print(Dbl2)

    Dbl1.Save('Dbl2.json')
    Dbl1.Load('Dbl2.json')
'''


import json
import random
import operator


class TDbListException(Exception): ...


class TDbCond(list):
    # aCond is [ (operator.lt, Db1.Fields.GetNo('Age'), 40, True), (...) ]
    def Add(self, aOp: operator, aFieldNo: int, aVal, aRes: bool):
        self.append([aOp, aFieldNo, aVal, aRes])

    def AddField(self, aOp: str, aField: tuple, aVal, aRes: bool):
        Dbl, Name = aField
        Func = getattr(operator, aOp, None)
        self.Add(Func, Dbl.Fields.GetNo(Name), aVal, aRes)

    def AddFields(self, aConds: list):
        for x in aConds:
            self.AddField(*x)
        return self

    def Find(self, aData: list) -> bool:
        for Func, FieldNo, Val, CmpRes in self:
            if (not Func(aData[FieldNo], Val) == CmpRes):
                return False
        return True


class TDbFields(dict):
    def __init__(self, aFields: tuple = ()):
        super().__init__()

        self.IdxOrd = {}
        self.AddList(aFields)

    def Add(self, aName: str, aType: type = str, aDef = None):
        if (self.get(aName)):
            raise TDbListException('field already exists %s' % (aName))

        if (aDef):
            if (not isinstance(aDef, aType)):
                raise TDbListException('types mismatch %s, %s' % (aType, aDef))
        else:
            Def = {'str': '', 'int': 0, 'float': 0.0, 'bool': False, 'tuple': (), 'list': [], 'dict': {}, 'set': set()}
            aDef = Def.get(aType.__name__, object)

        Len = len(self)
        self[aName] = (Len, aType, aDef)
        self.IdxOrd[Len] = (aName, aType, aDef)

    def AddList(self, aFields: list):
        for Field in aFields:
            self.Add(*Field)

    def AddAuto(self, aFields: list, aData: list):
        for Idx, Val in enumerate(aFields):
            if (aData):
                self.Add(Val, type(aData[Idx]))
            else:
                self.Add(Val)

    def Export(self) -> list:
        Items = sorted(self.items(), key = lambda k: k[1][0])
        return [(Key, Type.__name__, Def) for Key, (No, Type, Def) in Items]

    def Import(self, aFields: list):
        Data = [(Name, type(eval(Type)()), Def) for Name, Type, Def in aFields]
        self.AddList(Data)

    def GetFields(self, aFields: list) -> 'TDbFields':
        if (not aFields):
            aFields = self.GetList()

        Res = TDbFields()
        for Name in aFields:
            _, Type, Def = self[Name]
            Res.Add(Name, Type, Def)
        return Res

    def GetList(self) -> list:
        return [self.IdxOrd[i][0] for i in range(len(self))]

    def GetNo(self, aName: str) -> int:
        return self[aName][0]


class TDbRec(list):
    def __init__(self, aParent: 'TDbList'):
        super().__init__()
        self.Parent = aParent

    def Find(self, aCond: TDbCond) -> bool:
        return aCond.Find(self)

    def Flush(self):
        self.Parent.Data[self.Parent._RecNo] = self.copy()

    def Init(self):
        Fields = self.Parent.Fields
        Rec = [None] * len(Fields)
        for Idx, _ in enumerate(Fields):
            Rec[Idx] = Fields.IdxOrd[Idx][2]
        super().__init__(Rec)

    def GetField(self, aName: str) -> object:
        Idx = self.Parent.Fields.GetNo(aName)
        return self[Idx]

    def SetField(self, aName: str, aValue: object):
        Idx = self.Parent.Fields.GetNo(aName)
        if (self.Parent.Safe):
            if (not isinstance(aValue, self.Parent.Fields[aName][1])):
                raise TDbListException('types mismatch %s, %s' % (type(aValue), self.Parent.Fields[aName]))
        self[Idx] = aValue

    def SetData(self, aData: list):
        if (self.Parent.Safe):
            IdxOrd = self.Parent.Fields.IdxOrd
            for Idx, Field in enumerate(aData):
                if (not isinstance(Field, IdxOrd[Idx][1])):
                    raise TDbListException('types mismatch %s, %s' % (type(Field), IdxOrd[Idx]))
        super().__init__(aData)

    def GetAsDict(self) -> dict:
        return {Key: self[Val[0]] for Key, Val in self.Parent.Fields.items()}

    def GetAsSql(self) -> str:
        Res = []
        for _, (FNo, FType, _) in self.Parent.Fields.items():
            if (FType == bool):
                Val = str(self[FNo])
            elif (FType in [int, float]):
                Val = str(self[FNo])
            else:
                Val = "'" + str(self[FNo]) + "'"
            Res.append(Val)
        return ', '.join(Res)

    def SetAsDict(self, aData: dict):
        NotUsed = [self.SetField(Key, Val) for Key, Val in aData.items()]
        self.Flush()

    def GetAsTuple(self) -> list:
        return [(Key, self[Val[0]]) for Key, Val in self.Parent.Fields.items()]

    def SetAsTuple(self, aData: tuple):
        NotUsed = [self.SetField(Key, Val) for Key, Val in aData]
        self.Flush()


class TDbList():
    def __init__(self, aFields: list = [], aData: list = None):
        self.Tag = 0
        self.Data = []
        self._RecNo = 0
        self.Safe = True
        self.Fields = None
        self.Rec = TDbRec(self)
        self.Init(aFields, aData)

    def __len__(self):
        return self.GetSize()

    def __iter__(self):
        self._RecNo = -1
        return self

    def __next__(self):
        if (self._RecNo >= self.GetSize() - 1):
            raise StopIteration
        else:
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

        for Data in self.Data:
            for Idx, Val in enumerate(Data):
                Res[Idx] = max(Res[Idx], len(str(Val)))
        return Res

    def _Repr(self, aMaxLen: int = 20):
        FieldsLen = [3] + self._GetMaxLen()
        Fields = ['No'] + self.Fields.GetList()

        Format = [
            '%' + str(FieldsLen[Idx]) + 's '
            for Idx, Value in enumerate(Fields)
        ]
        Format = ''.join(Format)

        Res = []
        Res.append(Format % tuple(Fields))
        for Idx, Data in enumerate(self.Data):
            DataTrim = [str(x)[:aMaxLen] for x in Data]
            Res.append(Format % tuple([Idx] + DataTrim))
        return '\n'.join(Res)

    def _DbExp(self, aData: list, aFields: list) -> 'TDbList':
        Res = TDbList()
        Res.Fields = self.Fields.GetFields(aFields)
        Res.Data = aData
        return Res

    def _RecInit(self):
        if (not self.IsEmpty()):
            self.Rec.SetData(self.Data[self._RecNo])

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
        return self.Rec

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
        Res = [D[FieldNo] for D in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def ExportData(self, aFields: list = [], aCond: TDbCond = None, aRecNo: tuple = (0, -1)) -> list:
        Start, Finish = aRecNo
        if (Finish == -1):
            Finish = self.GetSize()

        if (aFields):
            FieldsNo = [self.Fields.GetNo(F) for F in aFields]
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

    def ImportList(self, aField: str, aData: list):
        Rec = TDbRec(self)
        Rec.Init()
        FieldNo = self.Fields.GetNo(aField)
        for Val in aData:
            Arr = Rec.copy()
            Arr[FieldNo] = Val
            self.Data.append(Arr)

    def ImportDbl(self, aDbl: 'TDbList', aFields: list = [], aCond: TDbCond = None, aRecNo: tuple = (0, -1)):
        self.Data = aDbl.ExportData(aFields, aCond, aRecNo)
        self.Fields = aDbl.Fields.GetFields(aFields)
        self.Tag = aDbl.Tag
        return self

    def ImportPair(self, aData: dict, aKeyName: str, aFieldValue: tuple):
        self.Fields = TDbFields([(aKeyName, str), aFieldValue])
        self.Data = [[Key, Val] for Key, Val in aData.items()]
        return self

    def Import(self, aData: dict):
        self.Tag = aData.get('Tag')
        self.Data = aData.get('Data')
        self.Fields = TDbFields()
        self.Fields.Import(aData.get('Head'))
        self.RecNo = 0
        return self

    def SetData(self, aData: list):
        if (aData):
            if (len(aData[0]) != len(self.Fields)):
                raise TDbListException('fields count mismatch %s and %s' % (len(aData[0]), len(self.Fields)))

            if (self.Safe):
                for Rec in aData:
                    self.RecAdd(Rec)
            else:
                self.Data = aData
            self.RecNo = 0
        else:
            self.Empty()
        return

    def GetDiff(self, aField: str, aList: list) -> tuple:
        Set1 = set(self.ExportList(aField))
        Set2 = set(aList)
        return (Set1 - Set2, Set2 - Set1)

    def Find(self, aCond: TDbCond) -> int:
        for i in range(self._RecNo, self.GetSize()):
            if (aCond.Find(self.Data[i])):
                return i

    def FindField(self, aName: str, aValue) -> int:
        FieldNo = self.Fields.GetNo(aName)
        for i in range(self._RecNo, self.GetSize()):
            if (self.Data[i][FieldNo] == aValue):
                return i

    def AddField(self, aFields: list = []):
        self.Fields.AddList(aFields)
        for Data in self.Data:
            for Field in aFields:
                Def = self.Fields[Field[0]][2]
                Data.append(Def)

    def Clone(self, aFields: list = [], aCond: TDbCond = None, aRecNo: tuple = (0, -1)) -> 'TDbList':
        Data = self.ExportData(aFields, aCond, aRecNo)
        return self._DbExp(Data, aFields)

    def Sort(self, aFields: list, aReverse: bool = False):
        if (len(aFields) == 1):
            FieldNo = self.Fields.GetNo(aFields[0])
            self.Data.sort(key=lambda x: (x[FieldNo]), reverse=aReverse)
        else:
            F = ''
            for Field in aFields:
                F += 'x[%s],' % self.Fields.GetNo(Field)
            Script = 'self.Data.sort(key=lambda x: (%s), reverse=%s)' % (F, aReverse)
            eval(Script)
        self.RecNo = 0

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecNo = 0

    def RecAdd(self, aData: list = []):
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
        with open(aFile, 'w') as F:
            if (aFormat):
                json.dump(self.Export(), F, indent=2, sort_keys=True, ensure_ascii=False)
            else:
                json.dump(self.Export(), F)

    def Load(self, aFile: str):
        with open(aFile, 'r') as F:
            Data = json.load(F)
            self.Import(Data)

'''
if (__name__ == '__main__'):
    Dbl1 = TDbList( [('User', str), ('Age', int), ('Male', bool, True)] )
    Data = [['User2', 22, True], ['User1', 11, False], ['User3', 33, True], ['User4', 44, True]]
    Dbl1.SetData(Data)
'''

