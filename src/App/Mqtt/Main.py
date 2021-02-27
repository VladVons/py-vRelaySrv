'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:.

https://github.com/beerfactory/hbmqtt
'''


import asyncio
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1
#
from Inc.Log  import Log
from Inc.Conf import Conf


Topic = 'vRelay/#'

class TMqtt():
    Cnt = 0

    async def Hanler(self, aPacket):
        self.Cnt += 1
        Log.Print(1, 'i', 'Hanler', '%d %s %s' % (self.Cnt, aPacket.variable_header.topic_name, aPacket.payload.data))

    async def Run(self):
        while True:
            Client = MQTTClient('vRelay-srv')
            await Client.connect('mqtt://' + Conf.Mqtt_Host)
            await Client.subscribe([(Topic, QOS_1)])

            try:
                while True:
                    Message = await Client.deliver_message()
                    await self.Hanler(Message.publish_packet)
            except ClientException as E:
                await Client.unsubscribe([Topic])
                await Client.disconnect()
                Log.Print(1, 'x', 'Run', E)
