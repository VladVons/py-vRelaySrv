'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:.

https://github.com/beerfactory/hbmqtt

error: Connection failed:
patch: hbmqtt/client.py connect()
        #except BaseException as be:
        except Exception as be:
'''


import asyncio
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1
#
from Inc.Conf import Conf
from IncP.Log  import Log


Topic = 'vRelay/#'

class TMqtt():
    Cnt = 0

    async def Hanler(self, aPacket):
        self.Cnt += 1
        Log.Print(1, 'i', 'Hanler', '%d %s %s' % (self.Cnt, aPacket.variable_header.topic_name, aPacket.payload.data))

    async def Run(self):
        while True:
            try:
                print('----11')
                Client = MQTTClient('vRelay-srv')
                await Client.connect('mqtt://' + Conf.Mqtt_Host)
                await Client.subscribe([(Topic, QOS_1)])

                while True:
                    print('----12')
                    Message = await Client.deliver_message()
                    await self.Hanler(Message.publish_packet)
            except Exception as E:
                print('----13')
                await Client.unsubscribe([Topic])
                await Client.disconnect()
                Log.Print(1, 'x', 'Run', E)

            #await asyncio.sleep(1)
