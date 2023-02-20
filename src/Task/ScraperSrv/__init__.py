from .Main import TScraperSrv

def Main(aConf) -> tuple:
    Obj = TScraperSrv(aConf)
    return (Obj, Obj.RunApp())
