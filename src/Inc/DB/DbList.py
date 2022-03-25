'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.24
License:     GNU, see LICENSE for more details
Description:
    Db1 = TDbList(['red', 'green', 'blue'])
    Data = [[21,22,23], [11,12,13], [111,121,131]]
    Db1.SetData(Data)

    print()
    print('GetSize:', Db1.GetSize())
    print('Data:', Db1.Data)
    print('Rec:', Db1.Rec)
    print('GetAsDict:', Db1.Rec.GetAsDict())
    print('GetAsTuple:', Db1.Rec.GetAsTuple())
    print('Json:', str(Db1))

    Db1.Sort('green', not True)
    for Idx, Val in enumerate(Db1):
        print(Idx, Val.Rec.GetByName('red'),  Val.Rec[0])

    Db1.Add()
    Db1.Rec.SetByName('red', 11)
    Db1.Flash()

    Db1.Data.append([22,33,44])

    Db2 = Db1.Clone(['green', 'blue'])
    print('Json:', str(Db2))
'''


import json


class TDbRec(list):
    def __init__(self, aHead: list):
        self.SetHead(aHead)

    def GetByName(self, aName: str) -> any:
        return self[self.Head[aName]]

    def SetByName(self, aName: str, aValue):
        self[self.Head[aName]] = aValue

    def Set(self, aList: list):
        self.clear()
        self.extend(aList)

    def SetHead(self, aFields: list):
        #self.Head = dict(zip(aFields, range(len(aFields))))
        self.Head = {Val: Idx for Idx, Val in enumerate(aFields)}

    def GetAsDict(self):
        return {Key: self[Val] for Key, Val in self.Head.items()}

    def GetAsTuple(self):
        return [(Key, self[Val]) for Key, Val in self.Head.items()]


class TDbList():
    def __init__(self, aHead: list):
        self.Rec = TDbRec(aHead)
        self.Data = []
        self._RecNo = 0

    def __str__(self):
        return json.dumps({'data': self.Data, 'head': self.Rec.Head})

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
        self.Rec.Set(self.Data[self._RecNo])

    def GetSize(self):
        return len(self.Data)

    def Clone(self, aFields: list):
        FieldNo = [self.Rec.Head[F] for F in aFields]
        #return [list(map(i.__getitem__, FieldNo)) for i in self.Data]
        Data = [[D[i] for i in FieldNo] for D in self.Data]

        Res = TDbList(aFields)
        Res.SetData(Data)
        return Res

    def Sort(self, aField: str, aReverse: bool = True):
        FieldNo = self.Rec.Head[aField]
        self.Data.sort(key=lambda x:x[FieldNo], reverse=aReverse)
        self.RecGo(0)

    def SetData(self, aList: list):
        self.Data = aList
        self.RecGo(0)

    def RecGo(self, aNo: int):
        self._RecNo = min(aNo, self.GetSize() - 1)
        self._RecInit()

    def Add(self):
        EmptyRec = [None for i in range(len(self.Rec.Head))]
        self.Data.append(EmptyRec)
        self.RecGo(self.GetSize())

    def Flash(self):
        self.Data[self._RecNo] = self.Rec
