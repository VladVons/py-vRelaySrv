'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details

pip install paho-mqtt
'''

import asyncio
import json
from socket import gethostname
from gmqtt import Client as MQTTClient
#
from Inc.Util.UNet import CheckHost
from IncP.DB.Relay_my import TDbApp
from IncP.Log import Log


Name  = 'vRelay'

class TMqtt():
    def __init__(self, aConf: dict):
        self.Conf = aConf
        self.Db = TDbApp(aConf.DbAuth)

    def on_connect(self, client, _flags, _rc, _properties):
        Msg = {'Data':{'Val':'-1'}}
        client.publish(Name + '/srv', json.dumps(Msg))

        client.subscribe(Name + '/#', qos=1)
        Log.Print(1, 'i', 'on_connect')

    def on_disconnect(self, _client, _packet):
        Log.Print(1, 'i', 'on_disconnect')

    async def on_message(self, _client, _topic, payload, _qos, _properties):
        #Log.Print(1, 'i', 'on_message. topic %s, payload %s, qos %s' % (topic, payload, qos))
        Msg = json.loads(payload.decode('utf-8'))
        Id = Msg.get('Id')
        Data = Msg.get('Data')
        Ok = False
        if (Id) and (Data):
            Ok = await self.Db.InsertDeviceByUniq(Id, Data.get('Owner'), Data.get('Val'))
            Log.Print(1, 'i', 'on_message', (Ok, Id, Data))

        if (not Ok):
            await self.Db.AddLog(1, "%s, %s" % (Id, Data))
            Log.Print(1, 'i', 'on_message bad', (Id, Data))

    async def Run(self):
        await self.Db.Connect()
        await self.Db.ExecFile('IncP/DB/Relay_my.sql')

        Client = MQTTClient('%s-srv-%s' % (Name, gethostname()))
        Client.on_message = self.on_message
        Client.on_connect = self.on_connect
        Client.on_disconnect = self.on_disconnect

        Port = self.Conf.get('Port', 1883)
        while True:
            if (not Client.is_connected) or (not await CheckHost(self.Conf.Host, Port, 3)):
                try:
                    await Client.disconnect()
                    await Client.connect(self.Conf.Host, Port, keepalive=60)
                except Exception as E:
                    Log.Print(1, 'x', 'Mqtt.Run()', aE = E)

            await asyncio.sleep(30)
