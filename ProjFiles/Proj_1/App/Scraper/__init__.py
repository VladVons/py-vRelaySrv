from .Api import Api

def Main(aConf) -> tuple:
    from .Main import TMain
    Api.Auth = aConf.SrvAuth

    Obj = TMain(aConf)
    return (Obj, Obj.Run())
