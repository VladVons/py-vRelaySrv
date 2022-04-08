'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.24
License:     GNU, see LICENSE for more details
Description:
'''


import json
import random
import operator as op

class TDbFields(dict):
    def __init__(self, aFields: tuple = ()):
        super().__init__()

        self.IdxOrd = {}
        self.AddFields(aFields)

    def Add(self, aName: str, aType: type = str, aDef = None):
        if (aDef):
            if (aType != type(aDef)):
                raise AssertionError('types mismatch %s, %s' % (aType, aDef))
        else:
            Def = {'str': '', 'int': 0, 'float': 0.0, 'bool': False, 'tuple': (), 'list': [], 'dict': {}, 'set': set()}
            aDef = Def.get(aType.__name__, object)

        Len = len(self)
        self[aName] = (Len, aType, aDef)
        self.IdxOrd[Len] = (aName, aType, aDef)

    def AddFields(self, aFields: list):
        for Field in aFields:
            self.Add(*Field)

    def Auto(self, aFields: list, aData: list):
        for i in range(len(aFields)):
            if (aData):
                self.Add(aFields[i], type(aData[i]))
            else:
                self.Add(aFields[i])

    def Export(self) -> list:
        Items = sorted(self.items(), key = lambda k: k[1][0])
        return [(Key, Type.__name__, Def) for Key, (No, Type, Def) in Items]

    def Import(self, aFields: list):
        Data = [(Name, type(eval(Type)()), Def) for Name, Type, Def in aFields]
        self.AddFields(Data)

    def GetList(self) -> list:
        return [self.IdxOrd[i][0] for i in range(len(self))]

    def GetNo(self, aName: str) -> int:
        return self[aName][0]


class TDbRec(list):
    def __init__(self, aParent: 'TDbList'):
        super().__init__()
        self.Parent = aParent

    def Flush(self):
        self.Parent.Data[self.Parent._RecNo] = self.copy()

    def GetField(self, aName: str) -> any:
        Idx = self.Parent.Fields.GetNo(aName)
        return self[Idx]

    def SetField(self, aName: str, aValue: any):
        Idx = self.Parent.Fields.GetNo(aName)
        if (self.Parent.Safe):
            if (type(aValue) != self.Parent.Fields[aName][1]):
                raise AssertionError('types mismatch %s, %s' % (type(aValue), self.Parent.Fields[aName]))
        self[Idx] = aValue

    def SetData(self, aData: list):
        if (self.Parent.Safe):
            IdxOrd = self.Parent.Fields.IdxOrd
            for Idx, Field in enumerate(aData):
                if (type(Field) != IdxOrd[Idx][1]):
                    raise AssertionError('types mismatch %s, %s' % (type(Field), IdxOrd[Idx]))
        super().__init__(aData)

    def GetAsDict(self) -> dict:
        return {Key: self[Val[0]] for Key, Val in self.Parent.Fields.items()}

    def SetAsDict(self, aData: dict):
        [self.SetField(Key, Val) for Key, Val in aData.items()]
        self.Flush()

    def GetAsTuple(self) -> list:
        return [(Key, self[Val[0]]) for Key, Val in self.Parent.Fields.items()]

    def SetAsTuple(self, aData: tuple):
        [self.SetField(Key, Val) for Key, Val in aData]
        self.Flush()

    def Init(self):
        Fields = self.Parent.Fields
        Rec = [None] * len(Fields)
        for Idx in range(len(Fields)):
            Rec[Idx] = Fields.IdxOrd[Idx][2]
        super().__init__(Rec)


class TDbList():
    def __init__(self, aFields: list = [], aData: list = None):
        self.Tag = 0
        self.Fields = None
        self.Data = []
        self.Rec = TDbRec(self)
        self.Safe = True
        self._Init(aFields, aData)

    def __iter__(self):
        return self

    def __next__(self):
        if (self._RecNo >= self.GetSize()):
            raise StopIteration
        else:
            self._RecInit()
            self._RecNo += 1
            return self

    def _DbExp(self, aData: list, aFields: list = []) -> 'TDbList':
        if (not aFields):
            aFields = self.Fields.keys()

        DbFields = TDbFields()
        for Field in aFields:
            F = self.Fields[Field]
            DbFields.Add(Field, F[1], F[2])

        Res = TDbList()
        Res.Fields = DbFields
        Res.Data = aData
        return Res 

    def _Init(self, aFields: list, aData: list = None):
        self.Fields = TDbFields()
        self.Fields.AddFields(aFields)
        self.SetData(aData)

    def _RecInit(self):
        if (not self.IsEmpty()):
            self.Rec.SetData(self.Data[self._RecNo])

    def GetSize(self) -> int:
        return len(self.Data)

    def IsEmpty(self) -> bool:
        return (self.GetSize() == 0)

    def Empty(self):
        self.Data = []
        self.RecGo(0)
        
    def DataExport(self) -> dict:
        return {'Data': self.Data, 'Head': self.Fields.Export(), 'Tag': self.Tag}

    def DataImport(self, aData: dict):
        self.Tag = aData['Tag']
        self.Data = aData['Data']
        self.Fields = TDbFields()
        self.Fields.Import(aData['Head'])

    def GetList(self, aField: str, aUniq = False) -> list:
        FieldNo = self.Fields.GetNo(aField)
        Res = [D[FieldNo] for D in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def DbClone(self, aFields: list, aRecNo: list = [0, -1]) -> 'TDbList':
        if (aRecNo[1] == -1):
            aRecNo[1] = self.GetSize()
        FieldNo = [self.Fields.GetNo(F) for F in aFields]
        #return [list(map(i.__getitem__, FieldNo)) for i in self.Data]
        Data = [[Val[i] for i in FieldNo] for Idx, Val in enumerate(self.Data) if (aRecNo[0] <= Idx <= aRecNo[1])]
        return self._DbExp(Data, aFields)

    def DbFilter(self, aCond: list) -> 'TDbList':
        # aCond = [ (operator.lt, Db1.Fields.GetNo('Age'), 40, True) ]
        def Find(aRec, aCond):
            for Func, FieldNo, Val, CmpRes in aCond:
                if (not Func(aRec[FieldNo], Val) == CmpRes):
                    return False
            return True

        Data = [Rec for Rec in self.Data if Find(Rec, aCond)]
        return self._DbExp(Data)

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
        self.RecGo(0)

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecGo(0)

    def AddList(self, aField: str, aData: list):
        Rec = TDbRec(self)
        Rec.Init()
        FieldNo = self.Fields.GetNo(aField)
        for Val in aData:
            Arr = Rec.copy()
            Arr[FieldNo] = Val  
            self.Data.append(Arr)

    def SetData(self, aData: list):
        if (aData):
            if (self.Safe):
                for Rec in aData:
                    self.RecAdd(Rec)
            else:
                self.Data = aData
            self.RecGo(0)
        else:
            self.Data = []

    def RecGo(self, aNo: int):
        if (aNo < 0):
            aNo = self.GetSize() + aNo
        self._RecNo = min(aNo, self.GetSize() - 1)
        self._RecInit()
        return self.Rec

    def RecAdd(self, aData: list = []):
        if (aData):
            self.Rec.SetData(aData)
        else:
            self.Rec.Init()
        self.Data.append(self.Rec.copy())
        self._RecNo = self.GetSize() - 1
        return self.Rec

    def RecPop(self) -> TDbRec:
        Res = TDbRec(self)
        Res.SetData(self.Data.pop())
        return Res

    def Save(self, aFile: str):
        with open(aFile, 'w') as F:
            Data = json.dumps(self.DataExport())
            F.write(Data)

    def Load(self, aFile: str):
        with open(aFile, 'r') as F:
            Data = json.load(F)
            self.DataImport(Data)

'''
if (__name__ == '__main__'):
    Db1 = TDbList( [('User', str), ('Age', int), ('Male', bool, True)] )
    Data = [['User2', 22, True], ['User1', 11, False], ['User3', 33, True]]
    Db1.Safe = True
    Db1.SetData(Data)

    Db1.RecAdd()
    #Db1.RecFlush()

    Db1.RecAdd()
    Db1.Rec.SetField('User', 'User4')
    Db1.Rec.SetField('Age', 20)
    Db1.Rec.SetField('Male', False)
    Db1.Rec.Flush()

    Db1.Data.append(['User5', 30, False])
    Db1.RecAdd(['User6', 40, True])
    Db1.Rec.Flush()

    Db1.RecAdd()
    Db1.Rec.SetAsDict({'User': 'User7', 'Age': 45, 'Male': True})
    Db1.Rec.Flush()

    Db1.RecGo(0)
    print()
    print('GetSize:', Db1.GetSize())
    print('Data:', Db1.Data)
    print('Rec:', Db1.Rec)
    print('Rec.GetAsDict:', Db1.Rec.GetAsDict())
    print('Rec.GetAsTuple:', Db1.Rec.GetAsTuple())
    print('Rec.GetList:', Db1.GetList('User', True))

    Db1.Sort(['User', 'Age'], True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetField('User'),  Val.Rec[1])

    print()
    Db3 = Db1.DbClone(['User', 'Age'], (0, 3))
    Db3.Shuffle()
    for Idx, Val in enumerate(Db3):
        print(Idx, Val.Rec.GetField('User'),  Val.Rec[1])

    Db3.RecGo(-2)
    print('Db3.Rec', Db3.Rec)

    print()
    import operator as op
    Cond = [ 
        (op.lt, Db1.Fields.GetNo('Age'), 40, True), 
        (op.eq, Db1.Fields.GetNo('Male'), True, True) 
    ]
    Db2 = Db1.DbFilter(Cond)
    print(Db2.Data)

    Db1.Save('Db2.json')
    Db1.Load('Db2.json')
'''