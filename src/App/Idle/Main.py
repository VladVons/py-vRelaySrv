'''
Author:      Vladimir Vons, Oster Inc.
Created:     2020.02.10
License:     GNU, see LICENSE for more details
Description:.
'''


import asyncio
#
from Inc.Conf import Conf
from Inc.Log  import Log

from IncP.Odbc  import TOdbc


class TIdle():
    async def Run(self, aSleep: float = 3):
        Odbc = TOdbc(Conf.AuthDb)

        CntLoop = 0
        while True:
            Log.Print(1, 'i', 'TIdle.Run', CntLoop)
            Rows = await Odbc.Query(
                'SELECT * \
                FROM Dict1 \
                ORDER BY ID DESC \
                LIMIT 1')
            print(Rows)

            CntLoop += 1
            await asyncio.sleep(aSleep)
