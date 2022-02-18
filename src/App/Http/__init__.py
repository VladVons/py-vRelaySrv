def Main(aConf) -> tuple:
    from .Main import THttp

    Obj = THttp()
    return (Obj, Obj.Run())
