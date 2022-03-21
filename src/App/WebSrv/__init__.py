def Main(aConf) -> tuple:
    from .Main import TWebSrv
    from App import ConfApp

    aConf.Def = ConfApp
    Obj = TWebSrv(aConf)
    return (Obj, Obj.Run())
