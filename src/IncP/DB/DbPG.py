'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.02.18
License:     GNU, see LICENSE for more details
Description:

pip3 install aiopg
'''


import aiopg
#
from .Db import TDb


class TDbPG(TDb):
    def __init__(self, aAuth: dict):
        self.Auth = aAuth

    async def Connect(self):
        if (self.Pool):
            await self.Pool.wait_closed()

        self.Pool = await aiomysql.create_pool(
                host=self.Auth.get('SERVER', 'localhost'),
                port=self.Auth.get('PORT', 3306),
                db=self.Auth.get('DATABASE'),
                user=self.Auth.get('USER'),
                password=self.Auth.get('PASSWORD')
                )

    async def Create(self):
        with open('IncP/DB/Struct.sql', 'r') as File:
            Query = File.read().strip()
            await self.Exec(Query)

    async def GetDeviceByUniq(self, aUniq: str, aAlias: str):
        Query = '''
            SELECT
                id
            FROM 
                devices
            WHERE
                (enable = 1) AND
                (uniq = '%s') AND
                (alias = '%s')
        ''' % (aUniq, aAlias)
        R = await self.Fetch(Query, True)
        #print('R', R, Query)
        return R

    async def InsertDeviceByUniq(self, aUniq: str, aAlias: str, aValue: float):
        Row = await self.GetDeviceByUniq(aUniq, aAlias)
        #print('---x1', aUniq, aAlias, Row)
        Res = (Row is not None)
        if (Row):
            Query = '''
                INSERT INTO devices_val(device_id, val)
                VALUES(%s, %s)
            ''' % (Row[0], aValue)
            await self.Exec(Query)
            return True

    async def GetDeviceValHourly(self, aId, aBegin, aEnd):
        #GetDeviceValHourly(5, datetime.date.today() - datetime.timedelta(days=7), datetime.datetime.now())
        Query = '''
            SELECT
                COUNT(*) Count,
                CONCAT(Year(create_date), ':', LPad(MONTH(create_date), 2, 0), ':', LPad(DAY(create_date), 2, 0), ' ', LPad(HOUR(create_date), 2, 0)) As Date,
                ROUND(AVG(val), 2) AS Val
            FROM
                devices_val
            WHERE
                (device_id = %d) AND
                (create_date BETWEEN '%s' AND '%s')
            GROUP BY
                Date
            ORDER BY
                Date
        ''' % (aId, aBegin, aEnd)
        return await self.Fetch(Query)

    async def GetDeviceCount(self, aBegin, aEnd):
        Query = '''
            SELECT
                COUNT(*) Count,
                device_id AS Device
            FROM
                devices_val
            WHERE
                (create_date BETWEEN '%s' AND '%s')
            GROUP BY
                Device
            ORDER BY
                Device
        ''' % (aBegin, aEnd)
        return await self.Fetch(Query)

    async def InsertLog(self, aType: int, aDescr: str):
        Query = '''
            INSERT INTO log(type_id, descr) VALUES(%s, "%s")
        ''' % (aType, aDescr)
        await self.Exec(Query)
