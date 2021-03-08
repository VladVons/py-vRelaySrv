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


class TDbOdbc():
    def __init__(self, aAuth: dict):
        self.Auth = ''
        for Key, Value in aAuth.items():
            self.Auth += '%s=%s;' % (Key, Value)

    async def Exec(self, aSql: str):
        async with aioodbc.connect(dsn=self.Auth) as Con:
            async with Con.cursor() as Cur:
                for Sql in filter(None, aSql.split(';')):
                    Sql = Sql.strip()
                    if (Sql):
                        await Cur.execute(Sql)
            await Con.commit()

    async def Fetch(self, aSql: str, aOne: bool = False):
        #async with aioodbc.connect(dsn=self.Auth, timeout=3) as Connect:
        async with aioodbc.connect(dsn=self.Auth) as Con:
            async with Con.cursor() as Cur:
                await Cur.execute(aSql)
                try:
                    if (aOne):
                        return await Cur.fetchone()
                    else:
                        return await Cur.fetchall()
                except: pass

    async def FetchWait(self, aSql: str, aTimeout = 5):
          try:
            return await asyncio.wait_for(self.Fetch(aSql), timeout=aTimeout)
          except asyncio.TimeoutError:
            pass
          except Exception as E:
            Log.Print(1, 'x', 'Exec()', E)
