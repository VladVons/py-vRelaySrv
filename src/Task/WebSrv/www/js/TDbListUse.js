const {TDbList, TDbRec}  = require('./TDbList');

Data1 = '{ \
    "head": ["user", "age", "male"],\
    "data": [\
        ["user2", 22, true],\
        ["user1", 11, false],\
        ["user3", 33, true],\
        ["user4", 44, true]\
    ]\
}';

//const Data2 = JSON.parse(Data1)
//const Dbl = new TDbList(Data2)
const Dbl = new TDbList().ImportStr(Data1)
console.log('GetSize', Dbl.GetSize())
console.log('Rec.AsDict', Dbl.Rec.GetAsDict())

Dbl.Sort('user')
for (let Rec of Dbl) {
    console.log(Rec.GetField('user'));
}

Dbl.RecAdd(['user5', 33, false])

Dbl.RecAdd().SetAsDict({'user': 'John', 'age': 55, 'male': true})

Rec = Dbl.RecAdd()
Rec.SetField('user', 'pink')

console.log('')
console.log('GetSize', Dbl.GetSize())
for (let Rec of Dbl) {
    console.log(Rec.Data);
}

Data = Dbl.Export()
console.log(Data)
