/*
opyright:    Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.03
Fork: Inc/DbList/DbList.py
*/


class TDbRec {
    constructor() {
        this.Data = []
        this.Fields = {}
    }

    GetAsDict() {
        let Res = {}
        for (const [Key, Val] of Object.entries(this.Fields)) {
            Res[Key] = this.Data[Val]
        }
        return Res
    }

    GetField(aName) {
        const Idx = this.Fields[aName]
        return this.Data[Idx]
    }

    GetFields() {
        return Object.keys(this.Fields)
    }

    Init(aFields, aData) {
        for (let i = 0; i < aFields.length; i++) {
            const x = aFields[i]
            this.Fields[x] = i
        }
        this.Data = aData
        return this
    }

    SetAsDict(aData) {
        for (const [Key, Val] of Object.entries(aData)) {
            this.SetField(Key, Val)
        }
        return this
    }

    SetField(aName, aVal) {
        const Idx = this.Fields[aName]
        this.Data[Idx] = aVal
    }
}


class TDbList {
    constructor(aData = {}) {
        //console.log('TDbList', aData)

        this.Empty()
        this.Rec = new TDbRec()

        if (Object.keys(aData).length > 0) {
            this.Import(aData)
        }
    }

    *[Symbol.iterator]() {
        for (let i = 0; i < this.GetSize(); i++) {
            this.RecNo = i
            yield this.Rec
        }
    }

    _RecInit() {
        if (this.GetSize() > 0) {
            this.Rec.Data = this.Data[this._RecNo]
        }
    }

    get RecNo() {
        return this._RecNo
    }

    set RecNo(aNo) {
        if (this.GetSize() == 0) {
            this._RecNo = 0
        }else{
            if (aNo < 0) {
                aNo = this.GetSize() + aNo
                this._RecNo = Math.min(aNo, this.GetSize() - 1)
            }
        }
        this._RecNo = aNo
        this._RecInit()
    }

    Empty() {
        this.Data = []
        this._RecNo = 0
    }

    Import(aData) {
        this.Data = aData['data']
        this.Rec.Init(aData['head'], this.Data[0])
        this.RecNo = 0
        return this
    }

    ImportStr(aData) {
        return this.Import(JSON.parse(aData))
    }

    Export() {
        return {'head': this.Rec.GetFields(), 'data': this.Data}
    }

    GetSize() {
        return this.Data.length
    }

    RecAdd(aData = []) {
        const Len = Object.keys(this.Rec.Fields).length
        if (aData.length == 0) {
            aData = Array(Len)
        }else{
            console.assert(aData.length == Len, 'wrong length')
        }

        this.Data.push(aData)
        this._RecNo = this.GetSize() - 1
        this._RecInit()
        return this.Rec
    }

    Sort(aField) {
        const Idx = this.Rec.Fields[aField]
        this.Data = this.Data.sort(
            function(aA, aB) {
                if (aA[Idx] < aB[Idx]) {
                    return -1
                }else if (aA[Idx] > aB[Idx]) {
                    return 1
                } else {
                    return 0
                }
        })
        this.RecNo = 0
    }
}

module.exports = { TDbList, TDbRec }
