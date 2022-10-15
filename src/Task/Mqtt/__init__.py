def Main(aConf) -> tuple:
    from .Main import TMqtt

    Obj = TMqtt(aConf)
    return (Obj, Obj.Run())
