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

    async def Handler(self, websocket, path):
        data = await websocket.recv()
        reply = f"Data recieved as:  {data}!"
        await websocket.send(reply)

    async def Run(self, aSleep: int = 30):
        while True:
            await websockets.serve(self.Handler, "localhost", 8082)
            await asyncio.sleep(aSleep)
