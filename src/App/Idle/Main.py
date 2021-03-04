'''
Author:      Vladimir Vons, Oster Inc.
Created:     2020.02.10
License:     GNU, see LICENSE for more details
Description:.
'''


import asyncio
#
from Inc.Conf import Conf
from IncP.Log import Log
#from IncP.DB.DbOdbc import TOdbc
from IncP.DB.DbMySql import TDbMySql


class TIdle():
    async def Run(self, aSleep: float = 3):
        Db = TDbMySql(Conf.AuthDb)

        CntLoop = 0
        while True:
            Log.Print(1, 'i', 'TIdle.Run', CntLoop)


            SQL = '''
                INSERT INTO %s 
                    (Item, Data, Prefix)
                VALUES 
                    ('%s', '%s', %d)
                ''' % ('Dict1', 'Item_1', 'Value_1', 1)
            await Db.Exec(SQL)

            SQL = '''
                SELECT
                    *
                FROM
                    Dict1
                 ORDER BY
                    ID DESC
                 LIMIT 1
                '''
            Rows = await Db.Exec(SQL)
            print(Rows)

            CntLoop += 1
            await asyncio.sleep(aSleep)
