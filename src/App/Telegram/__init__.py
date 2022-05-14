def Main(aConf) -> tuple:
    from .Main import TMain

    Obj = TMain(aConf)
    return (Obj, Obj.Run())
