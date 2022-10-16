from .Api import Api

def Main(aConf) -> tuple:
    from .Main import TWebSrv
    from Task import ConfTask

    Api.WebClient.Auth = aConf.SrvAuth
    aConf.Def = ConfTask
    Obj = TWebSrv(aConf)
    return (Obj, Obj.Run())
