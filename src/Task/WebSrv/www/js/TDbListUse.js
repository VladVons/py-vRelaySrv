const {TDbList, TDbRec}  = require('./TDbList')

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
const Dbl = new TDbList().ImportStr(Data1)
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
console.log('GetSize', Dbl.GetSize())
Dbl.Sort('user')
for (let Rec of Dbl) {
    console.log(Rec.Data)
}

console.log('')
console.log('Export')
Data = Dbl.Export()
console.log(Data)
