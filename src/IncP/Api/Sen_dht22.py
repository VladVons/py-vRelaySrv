'''
Author:      Vladimir Vons, Oster Inc
Created:     2018.02.11
License:     GNU, see LICENSE for more details
Description: micropython ESP8266
             DHT22 temperature-humidity sensor

https://forum.micropython.org/viewtopic.php?f=14&t=4876&p=28035#p28035
https://forum.micropython.org/viewtopic.php?f=15&t=4877&p=28043#p28043
'''


from IncP.Log import Log
from IncP.Api import TApiBase
from IncP.Dev.Sen_dht22 import DHT22


class TApi(TApiBase):
    Param = {
        'pin': 14
    }

    async def Exec(self, aPin: int) -> dict:
        try:
            Obj = DHT22(aPin)
            R = await Obj.Get()
        except Exception as E:
            Log.Print(1, 'x', 'sen_dht22', E)
            R = [None, None]
        return {'temperature': R[0], 'humidity': R[1]}

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['pin'])
