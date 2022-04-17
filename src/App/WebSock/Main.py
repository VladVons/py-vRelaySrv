'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.04.17
License:     GNU, see LICENSE for more details
Description:
'''

import asyncio
import websockets


class TWebSock():
    def __init__(self, aConf: dict):
        self.Conf = aConf

    async def Handler(self, aWebSocket, aPath):
        Data = await aWebSocket.recv()
        Reply = f'Path: {aPath}, Data: {Data}'
        print(Reply)
        await aWebSocket.send(Reply)
        pass

    async def Run(self):
        await websockets.serve(self.Handler, 'localhost', 8082)

        while True:
            await asyncio.sleep(60)