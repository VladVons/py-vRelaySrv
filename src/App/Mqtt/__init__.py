def Main(aConf) -> tuple:
    from .Main import TMqtt

    Obj = TMqtt()
    return (Obj, Obj.Run())
