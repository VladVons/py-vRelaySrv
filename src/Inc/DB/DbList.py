'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.24
License:     GNU, see LICENSE for more details
Description:
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

    Db1.Sort('User', True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetField('User'),  Val.Rec[1])

    print()
    Db2 = Db1.Filter([ (operator.lt, 1, 21, True) ])
    print(Db2.GetData())

    print()
    Db3 = Db1.Clone(['User', 'Age'], (0, 3))
    Db3.Shuffle()
    for Idx, Val in enumerate(Db3):
        print(Idx, Val.Rec.GetField('User'),  Val.Rec[1])

    Db3.RecGo(-2)
    print('Db3.Rec', Db2.Rec)
'''


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

    def GetList(self) -> list:
        return [self.IdxOrd[i][0] for i in range(len(self))]


class TDbRec(list):
    def __init__(self, aParent: 'TDbList'):
        super().__init__()
        self.Parent = aParent

    def Flush(self):
        self.Parent.Data[self.Parent._RecNo] = self.copy()

    def GetField(self, aName: str) -> any:
        Idx = self.Parent.Fields[aName][0]
        return self[Idx]

    def SetField(self, aName: str, aValue: any):
        Idx = self.Parent.Fields[aName][0]
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
        
    def GetData(self) -> dict:
        return {'Data': self.Data, 'Head': self.Fields, 'Tag': self.Tag}

    def GetList(self, aField: str, aUniq = False) -> list:
        FieldNo = self.Fields[aField][0]
        Res = [D[FieldNo] for D in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def Clone(self, aFields: list, aRecNo: list = [0, -1]) -> 'TDbList':
        if (aRecNo[1] == -1):
            aRecNo[1] = self.GetSize()
        FieldNo = [self.Fields[F][0] for F in aFields]
        #return [list(map(i.__getitem__, FieldNo)) for i in self.Data]
        Data = [[Val[i] for i in FieldNo] for Idx, Val in enumerate(self.Data) if (aRecNo[0] <= Idx <= aRecNo[1])]

        DbFields = TDbFields()
        for Field in aFields:
            F = self.Fields[Field]
            DbFields.Add(Field, F[1], F[2])
        Res = TDbList(DbFields)
        Res.SetData(Data)
        return Res 

    def Filter(self, aCond: list) -> 'TDbList':
        # aCond = [ (operator.eq, FieldNo, 'hello', True) ]
        def Find(aRec, aCond):
            for Func, Idx, Val, CmpRes in aCond:
                if (not Func(aRec[Idx], Val) == CmpRes):
                    return False
            return True

        Data = [Rec for Rec in self.Data if Find(Rec, aCond)]
        Res = TDbList()
        Res.Fields = self.Fields.copy()
        Res.Data = Data
        return Res


    def Sort(self, aField: str, aReverse: bool = False):
        FieldNo = self.Fields[aField][0]
        self.Data.sort(key=lambda x:x[FieldNo], reverse=aReverse)
        self.RecGo(0)

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecGo(0)

    def AddList(self, aField: str, aData: list):
        Rec = TDbRec(self)
        Rec.Init()
        FieldNo = self.Fields[aField][0]
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
