/*
opyright:    Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.03
*/


class TDbFields {
    constructor(aFields = []) {
        this.Data = {}
        this.IdxOrd = {}
        this.AddList(aFields)
    }

    Add(aName, aType, aDef) {
        var Def = {'str': '', 'int': 0, 'float': 0.0, 'bool': false, 'tuple': [], 'list': [], 'dict': {}}
        aDef = Def[aType]
        var Len = Object.keys(this.Data).length
        this.Data[aName] = [Len, aType, aDef]
        this.IdxOrd[Len] = [aName, aType, aDef]
    }

    AddList(aFields) {
        aFields.forEach((aItem) => {
            this.Add(aItem[0], aItem[1], aItem[2])
        })
    }

    GetNo(aName) {
        return this.Data[aName][0]
    }
}

class TDbRec {
    constructor(aParent) {
        this.Parent = aParent
        this.Data = []
    }

    Flush() {
        this.Parent.Data[this.Parent.RecNo] = this.Data
    }

    SetData(aData) {
        this.Data = aData
    }

    Init() {
        var Fields = this.Parent.Fields
        var Len = Object.keys(Fields.Data).length
        this.Data = new Array(Len)
        for (let i = 0; i < Len; i++) {
            this.Data[i] = Fields.IdxOrd[i][2]
        }
    }

    GetField(aName) {
        var Idx = this.Parent.Fields.GetNo(aName)
        return this.Data[Idx]
    }

    SetField(aName, aValue) {
        var Idx = this.Parent.Fields.GetNo(aName)
        this.Data[Idx] = aValue
    }
}


class TDbList {
    constructor(aData = {}) {
        //console.log('TDbList', aData)

        this.Empty()
        this.Rec = new TDbRec(this)

        if (Object.keys(aData).length > 0) {
            this.Import(aData)
        }
    }

    _RecInit() {
        if (! this.IsEmpty()) {
            this.Rec.SetData(this.Data[this.RecNo])
        }
    }

    IsEmpty() {
        return (this.GetSize() == 0)
    }

    Empty() {
        this.Data = []
        this.RecNo = 0
    }

    Import(aData) {
        this.Tag = aData['Tag']
        this.Data = aData['Data']
        this.Fields = new TDbFields(aData['Head'])
        this.RecGo(0)
    }

    GetSize() {
        return this.Data.length
    }

    RecGo(aNo) {
        if (this.IsEmpty()) {
            this.RecNo = 0
        }else{
            if (aNo < 0) {
                aNo = this.GetSize() + aNo
                this.RecNo = Math.min(aNo, this.GetSize() - 1)
            }
        }
        this.RecNo = aNo
        this._RecInit()
    }

    RecAdd(aData = []) {
        if (aData.length > 0) {
            this.Rec.SetData(aData)
        } else {
            this.Rec.Init()
        }

        this.Data.push(this.Rec)
        this.RecNo = this.GetSize() - 1
        return this.Rec
    }

    Shuffle() {
        this.Data = this.Data.sort(() => {
            const Rand = Math.random() > 0.5
            return Rand ? 1 : -1
        })
        this.RecGo(0)
        return this.Rec
    }
}


/*
Data1 = '{"Data": [["User2", 22, true], ["User1", 11, false], ["User3", 33, true], ["User4", 44, true]], "Head": [["User", "str", ""], ["Age", "int", 0], ["Male", "bool", true]], "Tag": 1}'
Data2 = JSON.parse(Data1)
DbL = new TDbList(Data2)
console.log('size', DbL.GetSize())
DbL.RecGo(-1)
console.log('Field', DbL.Rec.GetField('User'))
DbL.RecAdd(['User5', 33, false])
DbL.RecAdd()
DbL.Rec.SetField('User', 'Pink')
DbL.Rec.Flush()
console.log('size', DbL.GetSize())
console.log('end')
*/
