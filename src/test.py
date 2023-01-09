import asyncio
import json
#
from IncP.DB.DbPg import TDbPg
from IncP.DB.DbModel import TDbModel
from Inc.Util.Obj import DeepGet, DeepGetMask

DbAuth = {
    'Server': 'localhost',
    'Database': 'shop2',
    'User': 'admin',
    'Password': '098iop'
}

async def Test_01():
    DBModel = TDbModel('IncP/DB/Model')
    DBModel.LoadModel('DocSale')
    for i, x in enumerate(DBModel.Tables):
        print(i+1, x)
    pass

    #DbApp = TDbPg(DbAuth)
    #await DbApp.Connect()

    #await DbApp.Close()


#asyncio.run(Test_01())


with open ('IncP/DB/Model/RefProduct/Meta1.json', 'r') as f:
    Data = json.load(f)
#q1 = DeepGet(Data, 'table.ref_product.foreign_key.tenant_id.table')
#q1 = DeepGet(Data, 'table.*.*.*.table')

#q1 = DeepGetMask(Data, ['table', 'ref_product', 'foreign_key', 'tenant_id', 'table'])
#q1 = DeepGetMask(Data, 'table.ref_product.foreign_key.tenant_id.table')
#q1 = DeepGetMask(Data, 'table.*.foreign_key.tenant_id.table')
#q1 = DeepGetMask(Data, 'table.*.foreign_key.*.table')
#q1 = DeepGetMask(Data, 'table.*.foreign_key.*')
#q1 = DeepGetMask(Data, ['table', 'ref_product', '.*', 'tenant_id', 'table'])
#q1 = DeepGetMask(Data, ['table', '.*duct$', '.*', '.*', 'table'])
#q1 = DeepGetMask(Data, ['table', '*', '*', '*', 'table'])
#q1 = DeepGetMask(Data, ['^table', '^ref', '.*', 'tenant_id', 'table'])
q1 = DeepGetMask(Data, ['^table', '^ref', '.*', 'tenant_id', 'table'])


# s = 'ww[4w'
# chars = '.*[(+'
# if any((RegChr in '.*[(+') for RegChr in s):
#     print('Found')
# else:
#     print('Not Found')
for x in q1:
    print(x)
