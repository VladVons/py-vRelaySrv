def Main(aConf) -> tuple:
    from .Main import TIdle

    Obj = TIdle()
    return (Obj, Obj.Run(aConf.get('Sleep', 1)))
