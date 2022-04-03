'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.24
License:     GNU, see LICENSE for more details
Description:
    Fields = ['red', 'green', 'blue']
    Data = [[21, 22, 23], [11, 12, 13], [111, 121, 131], [211,221,231], [31, 32, 33]]
    Db1 = TDbList(Data, Fields)
    #Db1.SetData(Data)

    Db1.RecAdd([1,2,3])
    Db1.RecFlush()

    Db1.RecAdd()
    Db1.Rec.SetField('red', 10)
    Db1.Rec.SetField('green', 20)
    Db1.Rec.SetField('blue', 30)
    Db1.RecFlush()

    Db1.Data.append([101, 102, 103])
    Db1.RecAdd([22, 33, 44])
    Db1.RecFlush()

    Db1.RecAdd()
    Db1.Rec.SetAsDict({'red': 250, 'green': 251, 'blue': 252})
    Db1.RecFlush()
    Db1.RecGo(0)

    print()
    print('GetSize:', Db1.GetSize())
    print('Data:', Db1.Data)
    print('Rec:', Db1.Rec)
    print('GetAsDict:', Db1.Rec.GetAsDict())
    print('GetAsTuple:', Db1.Rec.GetAsTuple())
    print('GetList:', Db1.GetList('green', True))

    #Db1.Sort('green', not True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetField('red'),  Val.Rec[1])

    print()
    Db2 = Db1.Clone(['red', 'green'], (0, 2))
    Db2.Shuffle()
    for Idx, Val in enumerate(Db2):
        print(Idx, Val.Rec.GetField('red'),  Val.Rec[1])

    Db2.RecGo(-2)
    print('Db2.Rec', Db2.Rec)
'''


import random


class TDbFields(dict):
    def __init__(self):
        self.IdxOrd = {}

    def Add(self, aName: str, aType: type, aDef = None):
        if (aDef):
            assert (type(aDef) == aType), 'types mismatch'
        else:
            Def = {'str': '', 'int': 0, 'float': 0.0, 'bool': False, 'tuple': (), 'list': [], 'dict': {}}
            aDef = Def.get(aType.__name__)

        Len = len(self)
        self[aName] = (Len, aType, aDef)
        self.IdxOrd[Len] = (aName, aType, aDef)

    def AddFields(self, aFields: dict):
        for Field in aFields:
            self.Add(Field)


class TDbRec(list):
    def __init__(self, aParent: 'TDbList'):
        self.Parent = aParent

    def SetHead(self, aFields: list):
        #self.Head = dict(zip(aFields, range(len(aFields))))
        self.Head = {Val: Idx for Idx, Val in enumerate(aFields)}

    def GetHead(self) -> list:
        return sorted(self.Head, key= self.Head.get)

    def GetField(self, aName: str) -> any:
        return self[self.Head[aName]]

    def SetField(self, aName: str, aValue: any):
        self[self.Head[aName]] = aValue

    def SetData(self, aData: list):
        IdxOrd = self.Parent.Fields.IdxOrd
        for Idx, Field in enumerate(aData):
            assert (type(Field) == IdxOrd[Idx][1]), 'types mismatch'
        self.clear()
        self.extend(aData)

    def SetAsDict(self, aData: dict):
        [self.SetField(Key, Val) for Key, Val in aData.items()]

    def GetAsDict(self) -> dict:
        return {Key: self[Val] for Key, Val in self.Head.items()}

    def GetAsTuple(self) -> list:
        return [(Key, self[Val]) for Key, Val in self.Head.items()]


class TDbList():
    def __init__(self, aFields: TDbFields):
        self.Tag = 0
        self.Data = []
        self.Fields = aFields
        self.Rec = TDbRec(self)

    def __iter__(self):
        return self

    def __next__(self):
        if (self._RecNo >= self.GetSize()):
            raise StopIteration
        else:
            self._RecInit()
            self._RecNo += 1
            return self

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
        return {'Data': self.Data, 'Head': self.Rec.Head, 'Tag': self.Tag}

    def GetList(self, aField: str, aUniq = False) -> list:
        FieldNo = self.Rec.Head[aField]
        Res = [D[FieldNo] for D in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def Clone(self, aFields: list, aRecNo: tuple = (0, -1)) -> 'TDbList':
        if (aRecNo[1] == -1):
            aRecNo[1] = self.GetSize()
        FieldNo = [self.Rec.Head[F] for F in aFields]
        #return [list(map(i.__getitem__, FieldNo)) for i in self.Data]
        Data = [[Val[i] for i in FieldNo] for Idx, Val in enumerate(self.Data) if (aRecNo[0] <= Idx <= aRecNo[1])]
        return TDbList(aFields, Data)

    def Sort(self, aField: str, aReverse: bool = True):
        FieldNo = self.Rec.Head[aField]
        self.Data.sort(key=lambda x:x[FieldNo], reverse=aReverse)
        self.RecGo(0)

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecGo(0)

    def AddList(self, aField: str, aData: list):
        Head = self.Rec.Head
        Blank = [None for i in range(len(self.Rec.Head))]
        for Val in aData:
            Arr = Blank.copy()
            Arr[Head[aField]] = Val  
            self.Data.append(Arr)

    def SetData(self, aData: list, aCheck: bool = True):
        if (aCheck):
            for Rec in aData:
                self.RecAdd(Rec)
        else:
            self.Data = aData
        self.RecGo(0)

    def RecGo(self, aNo: int):
        if (aNo < 0):
            aNo = self.GetSize() + aNo
        self._RecNo = min(aNo, self.GetSize() - 1)
        self._RecInit()

    def RecAdd(self, aData: list = []):
        if (not aData):
            aData = [None for i in range(len(self.Rec.Head))]
        assert (len(aData) == len(self.Rec.Head)), 'length mismatch'

        self.Data.append(aData)
        self.RecGo(self.GetSize())

    def RecFlush(self):
        self.Data[self._RecNo] = self.Rec.copy()

    def RecPop(self) -> TDbRec:
        Res = TDbRec(self.Rec.GetHead())
        Res.SetData(self.Data.pop())
        return Res

if (__name__ == '__main__'):
    Fields = TDbFields()
    Fields.Add('User', str)
    Fields.Add('Age', int)
    Fields.Add('Male', bool)

    Data = [['User1', 11, False], ['User2', 22, 1], ['User3', 33, True]]
    Db1 = TDbList(Fields)
    Db1.SetData(Data)
