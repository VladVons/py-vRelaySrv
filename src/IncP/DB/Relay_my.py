'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.03.08
License:     GNU, see LICENSE for more details

apt install python3-mysqldb
pip3 install aiomysql
'''


import aiomysql
#
from .Db import TDb, TDbSql


class TDbApp(TDb):
    def __init__(self, aAuth: dict):
        self.Auth = aAuth

    async def Connect(self):
        await self.Close()

        self.Pool = await aiomysql.create_pool(
            host = self.Auth.get('Server', 'localhost'),
            port = self.Auth.get('Port', 3306),
            db = self.Auth.get('Database'),
            user = self.Auth.get('User'),
            password = self.Auth.get('Password')
        )

    async def AddLog(self, aType: int, aDescr: str):
        Query = '''
            INSERT INTO log(type_id, descr) VALUES({Type}, "{Descr}")
        '''.format(Type=aType, Descr=aDescr)
        await self.Exec(Query)

    async def GetDeviceByUniq(self, aUniq: str, aAlias: str):
        Query = '''
            SELECT
                id
            FROM
                devices
            WHERE
                (enable = 1) AND
                (uniq = '{Uniq}') AND
                (alias = '{Alias}')
        '''.format(Uniq=aUniq, Alias=aAlias)
        return await self.Fetch(Query, True)

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
                (device_id = {Id}) AND
                (create_date BETWEEN '{Begin}' AND '{End}')
            GROUP BY
                Date
            ORDER BY
                Date
        '''.format(Id=aId, Begin=aBegin, End=aEnd)
        return await TDbSql(self).Load(Query)

    async def GetDeviceCount(self, aBegin, aEnd):
        Query = '''
            SELECT
                COUNT(*) Count,
                device_id AS Device
            FROM
                devices_val
            WHERE
                (create_date BETWEEN '{Begin}' AND '{End}')
            GROUP BY
                Device
            ORDER BY
                Device
        '''.format(Begin=aBegin, End=aEnd)
        return await TDbSql(self).Load(Query)
