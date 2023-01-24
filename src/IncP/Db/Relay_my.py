# Created: 2021.03.08
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# apt install python3-mysqldb
# pip3 install aiomysql


import aiomysql
#
from Inc.UtilP.Db.ADb import TADb
from Inc.UtilP.Db.DbSql import TDbSql


class TDbApp(TADb):
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
        return await self.Exec(Query)

    async def InsertDeviceByUniq(self, aUniq: str, aAlias: str, aValue: float):
        Row = await self.GetDeviceByUniq(aUniq, aAlias)
        Res = (Row is not None)
        if (Res):
            Query = '''
                INSERT INTO devices_val(device_id, val)
                VALUES(%s, %s)
            ''' % (Row[0], aValue)
            await self.Exec(Query)
            return True

    async def GetDeviceValHourly(self, aId, aBegin, aEnd):
        #GetDeviceValHourly(5, datetime.date.today() - datetime.timedelta(days=7), datetime.datetime.now())
        Query = f'''
            SELECT
                COUNT(*) Count,
                CONCAT(Year(create_date), ':', LPad(MONTH(create_date), 2, 0), ':', LPad(DAY(create_date), 2, 0), ' ', LPad(HOUR(create_date), 2, 0)) As Date,
                ROUND(AVG(val), 2) AS Val
            FROM
                devices_val
            WHERE
                (device_id = {aId}) AND
                (create_date BETWEEN '{aBegin}' AND '{aEnd}')
            GROUP BY
                Date
            ORDER BY
                Date
        '''
        return await TDbSql(self).Exec(Query)

    async def GetDeviceCount(self, aBegin, aEnd):
        Query = f'''
            SELECT
                COUNT(*) Count,
                device_id AS Device
            FROM
                devices_val
            WHERE
                (create_date BETWEEN '{aBegin}' AND '{aEnd}')
            GROUP BY
                Device
            ORDER BY
                Device
        '''
        return await TDbSql(self).Exec(Query)
