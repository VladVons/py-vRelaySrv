from Inc.Plugin import TPlugin
from Inc.UtilP.Db.DbSql import TDbSql
from Inc.UtilP.Db.DbPg import TDbPg
from IncP.Log import Log


class TDbModel(TPlugin):
    def __init__(self, aDir: str, aDb: TDbPg):
        super().__init__(aDir)
        self.Db = aDb

    def _Create(self, aMod: object, aPath: str) -> object:
        Res = aMod.TMain()
        Res.Db = self.Db
        return Res
