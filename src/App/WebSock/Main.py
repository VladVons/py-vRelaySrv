'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.04.17
License:     GNU, see LICENSE for more details
Description:
'''

import asyncio
import websockets
from IncP.Log import Log


class TWebSock():
    def __init__(self, aConf: dict):
        self.Conf = aConf

    async def Task2(self, aWebSocket, aCnt):
        for i in range(aCnt):
            Msg = 'Task2 %s' % i
            print(Msg)
            await aWebSocket.send(Msg)
            await asyncio.sleep(3)

    async def Api(self, aWebSocket, aPath: str):
        print('Api', aWebSocket, aPath)
        recv_text = await aWebSocket.recv()
        print("recv_text:", aWebSocket.pong, recv_text)

        response_text = f"Server return: {recv_text}"
        print("response_text:", response_text)
        await aWebSocket.send(response_text)

    async def Handler(self, aWebSocket, aPath: str):
        print('Handler start')
        asyncio.create_task(self.Task2(aWebSocket, 100))
        while True:
            print('Handler loop')
            try:
                await self.Api(aWebSocket, aPath)
            except (websockets.ConnectionClosed, websockets.InvalidState):
                print("Connection closed", aPath)
                break
            except Exception as E:
                print("Exception:", E)
                await asyncio.sleep(1)

    async def Run(self):
        Port = self.Conf.get('Port', 8082)
        Log.Print(1, 'i', 'Run() listen websocket port %s' % (Port))
        await websockets.serve(self.Handler, 'localhost', Port)
