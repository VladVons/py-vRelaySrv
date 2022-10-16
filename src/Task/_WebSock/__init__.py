from .Main import TWebSock


def Main(aConf) -> tuple:
    Obj = TWebSock(aConf)
    return (Obj, Obj.Run())
