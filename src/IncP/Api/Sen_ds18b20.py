'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2018.06.18
License:     GNU, see LICENSE for more details
Description: micropython ESP8266
             DS1820 temperature sensor
'''


import binascii

from IncP.Log import Log
from IncP.Dev.Sen_ds18b20 import DS1820
from IncP.Api import TApiBase


class TApi(TApiBase):
    Param = {
        'pin': 14,
        'id': ''
    }

    async def Exec(self, aPin: int, aIDs: list) -> dict:
        HexID = []
        for ID in aIDs:
            HexID.append(binascii.unhexlify(ID))

        R = []
        try:
            Obj = DS1820(aPin)
            Data = await Obj.Get(HexID)
            for Item in Data:
                R.append({'id':binascii.hexlify(Item['id']), 'value':Item['value']})
        except Exception as E:
            Log.Print(1, 'x', 'Sen_ds18b20', E)
        return R

    async def Query(self, aData: dict) -> dict:
        Pin = self.Get(aData, 'pin')
        Id  = self.Get(aData, 'id')
        if (Id):
            Arr = Id.split(',')
        else:
            Arr = []
        return await self.Exec(Pin, Arr)
