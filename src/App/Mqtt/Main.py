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
    async def Run(self):
        while True:
            Client = MQTTClient('vRelay-srv')
            await Client.connect('mqtt://' + Conf.Mqtt_Host)
            await Client.subscribe([(Topic, QOS_1)])

            try:
                i = 0
                while True:
                    Message = await Client.deliver_message()
                    Packet = Message.publish_packet
                    print(f"{i}:  {Packet.variable_header.topic_name} => {Packet.payload.data}")
                    i += 1
            except ClientException as E:
                await Client.unsubscribe([Topic])
                await Client.disconnect()
                Log.Print(1, 'x', 'Run', E)
