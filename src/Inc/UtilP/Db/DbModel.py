from Inc.Plugin import TPlugin
from Inc.UtilP.Db.DbMeta import TDbMeta
#from Inc.UtilP.Db.DbSql import TDbSql
#from IncP.Log import Log


class TDbModel(TPlugin):
    def __init__(self, aDir: str, aDbMeta: TDbMeta):
        super().__init__(aDir)
        self.DbMeta = aDbMeta

    def _Create(self, aMod: object, aPath: str) -> object:
        Res = aMod.TMain()
        Res.DbMeta = self.DbMeta
        return Res
