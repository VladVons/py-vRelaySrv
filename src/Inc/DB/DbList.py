'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.24
License:     GNU, see LICENSE for more details
Description:
   Fields = ['red', 'green', 'blue']
    Data = [[21, 22, 23], [11, 12, 13], [111, 121, 131], [21, 22, 23]]
    Db1 = TDbList(Data, Fields)
    #Db1.SetData(Data)

    print()
    print('GetSize:', Db1.GetSize())
    print('Data:', Db1.Data)
    print('Rec:', Db1.Rec)
    print('GetAsDict:', Db1.Rec.GetAsDict())
    print('GetAsTuple:', Db1.Rec.GetAsTuple())
    print('GetList', Db1.GetList('green', True))
    print('Json:', str(Db1))

    Db1.Sort('green', not True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetField('red'),  Val.Rec[0])

    Db1.RecAdd()
    Db1.Rec.SetField('red', 11)
    Db1.RecFlush()

    #Db1.Data.append([22, 33, 44])
    Db1.RecAdd([22, 33, 44])
    Db1.RecFlush()

    Db2 = Db1.Clone(['green', 'blue'])
    Db2.Shuffle()
    print('Db2.Json:', str(Db2))

    Db2.RecGo(-2)
    print('Db2.Rec:', Db2.Rec)
'''


import json
import random


class TDbRec(list):
    def __init__(self, aHead: list):
        self.SetHead(aHead)

    def GetField(self, aName: str) -> any:
        return self[self.Head[aName]]

    def SetField(self, aName: str, aValue):
        self[self.Head[aName]] = aValue

    def SetData(self, aData: list):
        assert (len(aData) == len(self.Head)), 'length mismatch'
        self.clear()
        self.extend(aData)

    def SetHead(self, aFields: list):
        #self.Head = dict(zip(aFields, range(len(aFields))))
        self.Head = {Val: Idx for Idx, Val in enumerate(aFields)}

    def GetAsDict(self) -> dict:
        return {Key: self[Val] for Key, Val in self.Head.items()}

    def GetAsTuple(self) -> list:
        return [(Key, self[Val]) for Key, Val in self.Head.items()]


class TDbList():
    def __init__(self, aData: list, aHead: list):
        self.Data: list
        self.Rec: TDbRec

        self.SetData(aData, aHead)

    def __str__(self) -> str:
        return json.dumps(self.GetData())

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
        if (self.GetSize() > 0):
            self.Rec.SetData(self.Data[self._RecNo])

    def GetSize(self) -> int:
        return len(self.Data)

    def GetData(self) -> dict:
        return {'Data': self.Data, 'Head': self.Rec.Head}

    def GetList(self, aField: str, aUniq = False) -> list:
        FieldNo = self.Rec.Head[aField]
        Res = [D[FieldNo] for D in self.Data]
        if (aUniq):
            Res = list(set(Res))
        return Res

    def Clone(self, aFields: list) -> 'TDbList':
        FieldNo = [self.Rec.Head[F] for F in aFields]
        #return [list(map(i.__getitem__, FieldNo)) for i in self.Data]
        Data = [[D[i] for i in FieldNo] for D in self.Data]
        return TDbList(Data, aFields)

    def Sort(self, aField: str, aReverse: bool = True):
        FieldNo = self.Rec.Head[aField]
        self.Data.sort(key=lambda x:x[FieldNo], reverse=aReverse)
        self.RecGo(0)

    def Shuffle(self):
        random.shuffle(self.Data)
        self.RecGo(0)

    def SetData(self, aData: list, aHead: list = []):
        self.Data = aData
        if (aHead):
            self.Rec = TDbRec(aHead)
        self.RecGo(0)

    def RecGo(self, aNo: int):
        if (aNo < 0):
            aNo = self.GetSize() + aNo
        self._RecNo = min(aNo, self.GetSize() - 1)
        self._RecInit()

    def RecAdd(self, aData: list = []):
        if (not aData):
            aData = [None for i in range(len(self.Rec.Head))]
        self.Data.append(aData)
        self.RecGo(self.GetSize())

    def RecFlush(self):
        self.Data[self._RecNo] = self.Rec
