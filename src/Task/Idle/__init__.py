from .Main import TIdle


def Main(aConf) -> tuple:
    Obj = TIdle()
    return (Obj, Obj.Run(aConf.get('Sleep', 1)))
