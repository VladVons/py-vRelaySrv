def Main(aConf) -> tuple:
    from .Main import TWeb
    from App import ConfApp

    aConf.Def = ConfApp
    Obj = TWeb(aConf)
    return (Obj, Obj.Run())
