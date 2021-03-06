"""
Copyright:   (c) 2017, Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:

pip install paho-mqtt
"""

import json
import asyncio
from socket import gethostname

from gmqtt import Client as MQTTClient
#
from Inc.Conf import Conf
from IncP.Log import Log
from Inc.Util.UNet import CheckHost
from IncP.DB.DbMySql import TDbMySql


Name  = 'vRelay'

class TMqtt():
    def __init__(self):
        self.Db = TDbMySql(Conf.AuthDbMySql)

    def on_connect(self, client, flags, rc, properties):
        Msg = {'Data':{'Val':'Connect'}}
        client.publish(Name + '/srv', json.dumps(Msg))

        client.subscribe(Name + '/#', qos=1)
        Log.Print(1, 'i', 'on_connect')

    def on_disconnect(self, client, packet):
        Log.Print(1, 'i', 'on_disconnect')

    async def on_message(self, client, topic, payload, qos, properties):
        #Log.Print(1, 'i', 'on_message', 'topic %s, payload %s, qos %s' % (topic, payload, qos))
        Msg = json.loads(payload.decode('utf-8'))
        Id = Msg.get('Id')
        Data = Msg.get('Data')
        if (Id) and (Data):
            Ok = False
            #Ok = await self.Db.InsertDeviceByUniq(Id, Data.get('Owner'), Data.get('Val'))
            #Log.Print(1, 'i', 'on_message', (Ok, Id, Data))
            print('--- on_message', Ok, Id, Data)

    async def Run(self):
        await self.Db.Connect()

        Port = Conf.get('Mqtt_Port', 1883)

        Client = MQTTClient('%s-srv-%s' % (Name, gethostname()))
        Client.on_message = self.on_message
        Client.on_connect = self.on_connect
        Client.on_disconnect = self.on_disconnect

        while True:
            if (not Client.is_connected) or (not await CheckHost(Conf.Mqtt_Host, Port, 3)):
                try:
                    await Client.disconnect()
                    await Client.connect(Conf.Mqtt_Host, Port, keepalive=60)
                except Exception as E:
                    Log.Print(1, 'x', 'Mqtt.Run()', E)

            await asyncio.sleep(30)
