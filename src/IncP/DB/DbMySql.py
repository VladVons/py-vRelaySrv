
from .DbOdbc import TDbOdbc


class TDbMySql(TDbOdbc):
    def CreateDb(self):
        SQL = '''
            CREATE TABLE IF NOT EXISTS value (
                id          INTEGER UNSIGNED AUTO_INCREMENT, ?---
                created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_id   INTEGER UNSIGNED,
                value       FLOAT (10,3)
            )
            '''
        self.Exec(SQL)


        SQL = '''
            CREATE TABLE IF NOT EXISTS device_inf (
                id          INTEGER UNSIGNED AUTO_INCREMENT,
                name        TEXT,
                vendor      TEXT,
                min_val     FLOAT (10,3)
                max_val     FLOAT (10,3)
            )
            '''
        self.Exec(SQL)


        SQL = '''
            CREATE TABLE IF NOT EXISTS device (
                id          INTEGER UNSIGNED AUTO_INCREMENT,
                created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expired     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  ?--- дійсний до (проплачений або термін придатності) 
                enable      BOOLEAN DEFAULT TRUE,  ?--- (проплачений, термін придатності, заблокований)
                mac         CHAR(12), ?--- 80 % пристроїв мають Мак, але відсутній у UPS, азимут сонця ітд ...
                alias       TEXT, ?--- CHAR 16 якщо відсутній Мак, або його аліас 
                type_id     INTEGER UNSIGNED, ? --- вологість і температура в одному датчику
                device_inf  INTEGER UNSIGNED, 
                depart_id   INTEGER UNSIGNED, належність до обєкта склад1, склад2 
                org_id      INTEGER UNSIGNED, належність до організації 
            )
            '''
        self.Exec(SQL)

        SQL = '''
            CREATE TABLE IF NOT EXISTS type (
                id          INTEGER UNSIGNED AUTO_INCREMENT,
                name        TEXT
            )
            '''
        self.Exec(SQL)

        SQL = '''
            CREATE TABLE IF NOT EXISTS depart (
                id          INTEGER UNSIGNED AUTO_INCREMENT,
                name        TEXT,
            )
            '''
        self.Exec(SQL)

        SQL = '''
            CREATE TABLE IF NOT EXISTS org (
                id          INTEGER UNSIGNED AUTO_INCREMENT,
                name        TEXT,
                phone       TEXT, CHAR ? ---
            )
            '''
        self.Exec(SQL)

        SQL = '''
            CREATE TABLE IF NOT EXISTS payment (
                id          INTEGER UNSIGNED AUTO_INCREMENT,
                device_id   INTEGER UNSIGNED,
                created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sum         FLOAT (10,3)
            )
            '''
        self.Exec(SQL)
