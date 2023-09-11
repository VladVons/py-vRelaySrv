const {TDbList, TDbListEx}  = require('./TDbList')


//--- TDbList
Data1 = '{ \
    "head": ["user", "age", "male"],\
    "data": [\
        ["user4", 44, true],\
        ["user3", 33, true],\
        ["user2", 22, true],\
        ["user1", 11, false]\
    ]\
}'

//const Data2 = JSON.parse(Data1)
//const Dbl = new TDbList(Data2)
let Dbl = new TDbList().ImportStr(Data1)
console.log('GetSize', Dbl.GetSize())
console.log('Rec.AsDict', Dbl.Rec.GetAsDict())

for (let Rec of Dbl) {
    console.log(Rec.GetField('user'))
}

Dbl.RecAdd(['user5', 33, false])

Dbl.RecAdd().SetAsDict({'user': 'John', 'age': 55, 'male': true})

Rec = Dbl.RecAdd()
Rec.SetField('user', 'pink')
Rec.SetField('age', 41)

console.log('')
console.log('Export')
//Data = Dbl.Export()
Data = Dbl.ExportStr()
console.log(Data)

console.log('')
console.log('Clone')
Data = Dbl.Clone(['user', 'age']).Export()
console.log(Data)


//--- TDbListEx
Data1 = [
    {'user': 'user3', 'age': 37, 'male': true},
    {'user': 'user4', 'age': 47, 'male': false},
    {'user': 'user2', 'age': 27, 'male': true}
]
console.log('')
Dbl = new TDbListEx().ImportDict(Data1).Sort('age')
console.log('ExportStr', Dbl.ExportStr())
let q1 = Dbl.RecPop(1)
console.log(q1)
console.log('ExportStr', Dbl.ExportStr())
console.log('ExportDict', Dbl.ExportDict(['user', 'age']))
console.log('Done')
