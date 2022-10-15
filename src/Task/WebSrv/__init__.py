from .Api import Api

def Main(aConf) -> tuple:
    from .Main import TWebSrv
    from Task import ConfApp

    Api.WebClient.Auth = aConf.SrvAuth
    aConf.Def = ConfApp
    Obj = TWebSrv(aConf)
    return (Obj, Obj.Run())
