def Main(aConf) -> tuple:
    from .Main import TWebSock

    Obj = TWebSock(aConf)
    return (Obj, Obj.Run())
