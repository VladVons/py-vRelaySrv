from .Api import Api
from .Main import TMain

def Main(aConf) -> tuple:
    Api.WebClient.Auth = aConf.SrvAuth

    Obj = TMain(aConf)
    return (Obj, Obj.Run())
