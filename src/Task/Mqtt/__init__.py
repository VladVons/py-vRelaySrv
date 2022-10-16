from .Main import TMqtt


def Main(aConf) -> tuple:
    Obj = TMqtt(aConf)
    return (Obj, Obj.Run())
