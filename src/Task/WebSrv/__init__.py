from Inc.SrvWeb.SrvBase import TSrvConf
from Task import ConfTask
from .Api import Api
from .Main import TWebSrv


def Main(aConf) -> tuple:
    Api.WebClient.Auth = aConf.SrvAuth
    aConf.Def = ConfTask

    SrvConf = aConf.get('SrvConf', {})
    SrvConf = TSrvConf(**SrvConf)
    Obj = TWebSrv(SrvConf, aConf)
    return (Obj, Obj.RunApp())
