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
from gmqtt import Client as MQTTClient
#
from Inc.Conf import Conf
from IncP.Log import Log
from Inc.Util.UNet import CheckHost
from IncP.Odbc import TOdbc


Name  = 'vRelay'

class TMqtt():
    def __init__(self):
        self.Odbc = TOdbc(Conf.AuthDb)

    def on_connect(self, client, flags, rc, properties):
        client.publish(Name + '/srv', 'connect')
        client.subscribe(Name + '/#', qos=1)
        Log.Print(1, 'i', 'on_connect')

    def on_disconnect(self, client, packet):
        Log.Print(1, 'i', 'on_disconnect')

    async def on_message(self, client, topic, payload, qos, properties):
        Log.Print(1, 'i', 'on_message', 'topic %s, payload %s, qos %s' % (topic, payload, qos))
        Rows = await self.Odbc.Query(
                'SELECT * \
                 FROM Dict1 \
                 ORDER BY ID DESC \
                 LIMIT 1')
        print(Rows)

    async def Run(self):
        Port = Conf.get('Mqtt_Port', 1883)

        Client = MQTTClient(Name + '-srv')
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

            await asyncio.sleep(60)
