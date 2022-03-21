def Main(aConf) -> tuple:
    from .Main import TScraperSrv

    Obj = TScraperSrv(aConf)
    return (Obj, Obj.Run())
