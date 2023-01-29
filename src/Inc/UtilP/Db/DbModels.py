from Inc.Plugin import TPlugin
from Inc.UtilP.Db.DbMeta import TDbMeta


class TDbModels(TPlugin):
    def __init__(self, aDir: str, aDbMeta: TDbMeta):
        super().__init__(aDir)
        self.DbMeta = aDbMeta

    def _Create(self, aModule: object, aPath: str) -> object:
        Res = aModule.TMain(self.DbMeta, self.Dir + '/' + aPath)
        return Res
