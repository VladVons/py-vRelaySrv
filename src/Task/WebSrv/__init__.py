from Task import ConfTask
from .Api import Api
from .Main import TWebSrv


def Main(aConf) -> tuple:
    Api.WebClient.Auth = aConf.SrvAuth
    aConf.Def = ConfTask
    Obj = TWebSrv(aConf)
    return (Obj, Obj.Run())
