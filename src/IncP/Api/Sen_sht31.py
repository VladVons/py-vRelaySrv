'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2018.02.11
License:     GNU, see LICENSE for more details
Description: micropython ESP8266
             SHT31 temperature-humidity sensor
'''


import machine
#
from IncP.Log import Log
from IncP.Api import TApiBase
from IncP.Dev.Sen_sht31 import SHT31


class TApi(TApiBase):
    Param = {
        'scl': 5,
        'sda': 4
    }

    async def Exec(self, aScl: int, aSda: int) -> dict:
        i2c = machine.I2C(scl = machine.Pin(aScl), sda = machine.Pin(aSda))
        try:
            Obj = SHT31(i2c)
            R = await Obj.get_temp_humi()
        except Exception as E:
            Log.Print(1, 'x', 'Sen_sht31', E)
            R = [None, None]
        return {'temperature': R[0], 'humidity': R[1]}

    async def Query(self, aData: dict) -> dict:
        return await self.ExecDef(aData, ['scl', 'sda'])
