# Created: 2022.03.24
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from .DbCond import TDbCond


class TDbRec():
    def __init__(self):
        self.Data = []
        self.Fields = {}

    def Find(self, aCond: TDbCond) -> bool:
        return aCond.Find(self)

    def GetAsDict(self) -> dict:
        return dict(zip(self.Fields, self.Data))

    def GetAsSql(self) -> str:
        Res = [f"'{x}'" if (isinstance(x, str)) else str(x) for x in self.Data]
        return ', '.join(Res)

    def GetField(self, aName: str) -> object:
        Idx = self.Fields.get(aName)
        return self.Data[Idx]

    def GetAsTuple(self) -> list:
        return list(zip(self.Fields, self.Data))

    def SetAsDict(self, aData: dict) -> 'TDbRec':
        for Key, Val in aData.items():
            self.SetField(Key, Val)
        return self

    def SetAsRec(self, aRec: 'TDbRec', aFields: list) -> 'TDbRec':
        for Field in aFields:
            self.SetField(Field, aRec.GetField(Field))
        return self

    def SetAsTuple(self, aData: tuple) -> 'TDbRec':
        for Key, Val in aData:
            self.SetField(Key, Val)
        return self

    def SetField(self, aName: str, aValue: object) -> 'TDbRec':
        Idx = self.Fields.get(aName)
        self.Data[Idx] = aValue
        return self
