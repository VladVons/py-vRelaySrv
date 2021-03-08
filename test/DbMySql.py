
import aioodbc
# 
from .DbOdbc import TDbOdbc


class TDbMySql(TDbOdbc):
    async def CreateDb(self):
        # drop table devices_val, devices, departs, orgs

        SQLs = [
        '''
            CREATE TABLE IF NOT EXISTS `orgs` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `name`          VARCHAR(64),
                `phone`         VARCHAR(13),
                 PRIMARY KEY    (`id`)
            );
        ''',
        '''
            CREATE TABLE IF NOT EXISTS `departs` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `name`          VARCHAR(64),
                `orgs_id`       INTEGER UNSIGNED,
                PRIMARY KEY     (`id`),
                FOREIGN KEY     (orgs_id) REFERENCES orgs(id)
            );
        ''',
        '''
            CREATE TABLE IF NOT EXISTS `devices` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `expire_date`   DATE,
                `enable`        BOOLEAN DEFAULT TRUE,
                `uniq`          VARCHAR(16),
                `alias`         VARCHAR(16),
                `descr`         TEXT,
                `departs_id`    INTEGER UNSIGNED,
                PRIMARY KEY     (`id`),
                UNIQUE KEY      (`uniq`, `alias`),
                FOREIGN KEY     (departs_id) REFERENCES departs(id)
            );
        ''',
        '''
            CREATE TABLE IF NOT EXISTS `devices_val` (
                `id`            INTEGER UNSIGNED AUTO_INCREMENT,
                `create_date`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `devices_id`    INTEGER UNSIGNED,
                `val`           FLOAT(10,3),
                PRIMARY KEY     (`id`),
                FOREIGN KEY     (devices_id) REFERENCES devices(id)
            );
        '''
        ]

        async with aioodbc.connect(dsn=self.Auth) as Con:
            async with Con.cursor() as Cur:
                for Item in SQLs:
                    await Cur.execute(Item)
                await Con.commit()
