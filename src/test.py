#!/usr/bin/env python3

import asyncio
import datetime
#
from IncP.DB.DbMySql import TDbMySql
from Inc.Conf import Conf

class TClass1():
    async def Test1(self):
        Db = TDbMySql(Conf.AuthDbMySql)
        await Db.Connect()
        #Rows = await Db.GetHourlyVal(5, datetime.date.today(), datetime.datetime.now())
        Rows = await Db.GetValHourly(5, datetime.date.today() - datetime.timedelta(days=7), datetime.datetime.now())
        print(Rows)

        #await Db.CreateDb()
        #await Db.GetDeviceByUniq('f871e400', 'TSen_dht22_t')
        #await Db.GetIdByUniq('6d9dbc00', 'TSen_ds18b20')
        await Db.InsertDeviceByUniq('f871e400', 'TSen_dht22_t', 1.234)

    async def Prove(self):
        return

        Loops = 0
        while True:
            Loops += 1
            #print('Prove', Loops)
            await asyncio.sleep(5)

    async def Run(self):
        Task1 = asyncio.create_task(self.Prove())
        Task2 = asyncio.create_task(self.Test1())
        await asyncio.gather(Task1, Task2)


asyncio.run(TClass1().Run())
