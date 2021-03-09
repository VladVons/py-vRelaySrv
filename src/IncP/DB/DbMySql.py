
import aioodbc
# 
from .DbOdbc import TDbOdbc


class TDbMySql(TDbOdbc):
    async def CreateDb(self):
        # drop table devices_val, devices, departs, orgs

        Query = '''
            CREATE TABLE IF NOT EXISTS `orgs` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `name`          VARCHAR(64),
                `phone`         VARCHAR(13),
                 PRIMARY KEY    (`id`)
            );

            CREATE TABLE IF NOT EXISTS `departs` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `name`          VARCHAR(64),
                `orgs_id`       INTEGER UNSIGNED,
                PRIMARY KEY     (`id`),
                FOREIGN KEY     (orgs_id) REFERENCES orgs(id)
            );

            CREATE TABLE IF NOT EXISTS `devices` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `expire_date`   DATE,
                `enable`        BOOLEAN DEFAULT FALSE,
                `uniq`          VARCHAR(16),
                `alias`         VARCHAR(16),
                `descr`         TEXT,
                `departs_id`    INTEGER UNSIGNED,
                PRIMARY KEY     (`id`),
                UNIQUE KEY      (`uniq`, `alias`),
                FOREIGN KEY     (departs_id) REFERENCES departs(id)
            );

            CREATE TABLE IF NOT EXISTS `devices_val` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `devices_id`    INTEGER UNSIGNED,
                `val`           FLOAT(10,3),
                PRIMARY KEY     (`id`),
                FOREIGN KEY     (devices_id) REFERENCES devices(id)
            );
        '''

        await self.ExecScrypt(Query)

    async def GetDeviceByUniq(self, aUniq, aAlias):
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

    async def InsertDeviceByUniq(self, aUniq, aAlias, aValue):
        Row = await self.GetDeviceByUniq(aUniq, aAlias)
        if (Row):
            Query = '''
                INSERT INTO devices_val(devices_id, val)
                VALUES(%s, %s)
            ''' % (Row[0], aValue)
            await self.Exec(Query)
            return True
