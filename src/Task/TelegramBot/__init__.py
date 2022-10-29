from .Main import TMain


def Main(aConf) -> tuple:
    Obj = TMain(aConf)
    return (Obj, Obj.Run())
