import asyncio
import binascii
import random
from IncP.DB.Scraper_pg import TDbApp


DbAuth = {
    'Server': 'localhost',
    'Database': 'test1',
    'User': 'postgres',
    'Password': '19710819'
}

async def Test_A1():
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    DbFetch = await DbApp.GetSiteUrlCountForUpdate()
    await DbApp.Close()

    print()
    print('--x1', DbFetch.GetSize())
    print('--x2', DbFetch.Data)
    print('--x3', DbFetch.Rec)
    print('--x4', str(DbFetch))
    for Item in DbFetch:
        print(Item.Rec.GetByName('site.url'), Item.Rec[1])

async def Test_A2():
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()
    DbFetch = await DbApp.GetSiteUrlCountForUpdate()
    await DbApp.Close()

    print()
    for Item in DbFetch:
        print(Item.Rec.GetByName('site.url'),  Item.Rec.GetByName('url_count'))


def ListSearch():
    Data = [1,2,3,4,5,6,7,8,9,10]
    Arr = []
    for i in range(10000):
        #Data.rotate(2)
        Arr.append(Data)

    for Item in Arr:
        if (Item[2] == 4):
            print(Item)
            pass

def TestDbArr1():
    from Inc.DB.DbList import TDbList

    Fields = {'null': 0, 'one': 1, 'two': 2}
    Data = [[1,2,3], [3,4,5], [6,7,8]]
    Db = TDbList(Fields)
    Db.SetData(Data)

    print()
    print('--x1', Db.GetSize())
    print('--x2', Db.Data)
    print('--x3', Db.Rec)
    print('--x4', str(Db))
    #for Item in Db:
    #    print(Item.Rec.GetByName('one'),  Item.Rec[1])

    print(Db.GetData([0, 1]))

def TestDbArr2():
    from Inc.DB.DbList import TDbList

    Fields = {'null': 0, 'one': 1, 'two': 2}
    Data = [[1,2,3], [3,4,5], [6,7,8]]
    Db = TDbList(Fields)
    Db.Load(Data)

    print()
    print(Db.Rec.GetByName('one'), Db.Rec[1])
    for Item in Db:
        print(Item.Rec.GetByName('one'))

    print(str(Db))
    Db.Add()
    Db.Rec.SetByName('one', 11)
    Db.Flash()
    print(str(Db))



#asyncio.run(Test_A2())
TestDbArr1()


#Data = [[-2,1,5,4], [-2,1,5,4]]
#Fields = [0,1,3]
#c = [D for i, D in enumerate(Data) if i in Fields]
#print(c)
#c = [[D[i] for i in Fields] for D in Data]
#print(c)

#c = [list(map(i.__getitem__, Fields)) for i in Data]
#c = [list(map(i, Fields)) for i in Data]
#print(c)

#a = [-2, 1, 5, 3, 8, 5, 6]
#b = [0, 2, 5]
#c = [i for i in a if i in b]
#print(c)
