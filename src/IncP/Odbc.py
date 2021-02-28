'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:.

apt install python3-pyodbc unixodbc
apt install libsqliteodbc odbc-mariadb odbc-postgresql
cat /etc/odbcinst.ini
pip3 install aioodbc
'''


import asyncio
import aioodbc
#
from IncP.Log  import Log


class TOdbc():
    def __init__(self, aAuth: dict):
        self.Auth = ''
        for Key, Value in aAuth.items():
            self.Auth += '%s=%s;' % (Key, Value)

    async def _Query(self, aSql: str):
        #async with aioodbc.connect(dsn=self.Auth, timeout=3) as Connect:
        async with aioodbc.connect(dsn=self.Auth) as Connect:
            async with Connect.cursor() as Cursor:
                await Cursor.execute(aSql)
                return await Cursor.fetchall()

    async def Query(self, aSql: str, aTimeout = 5):
          try:
            return await asyncio.wait_for(self._Query(aSql), timeout=aTimeout)
          except asyncio.TimeoutError:
            pass
          except Exception as E:
            Log.Print(1, 'x', 'Query()', E)
