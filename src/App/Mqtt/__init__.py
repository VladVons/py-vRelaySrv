def Main():
    from .Main import TMqtt

    Obj = TMqtt()
    return (Obj, Obj.Run())
