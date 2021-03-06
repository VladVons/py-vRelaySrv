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


import aioodbc
#
from .Db import TDb


class TDbOdbc(TDb):
    def __init__(self, aAuth: dict):
        self.Auth = aAuth

    def _GetAuthStr(self, aAuth: dict) -> str:
        R = ''
        for Key, Value in aAuth.items():
            R += '%s=%s;' % (Key, Value)
        return R

    async def Connect(self):
        if (self.Pool):
            await self.Pool.wait_closed()

        self.Pool = await aioodbc.create_pool(dsn=self._GetAuthStr(self.Auth))
