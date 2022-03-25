'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.19
License:     GNU, see LICENSE for more details
Description:
'''


try:
  import asyncio
except:
  import uasyncio as asyncio


async def CheckHost(aHost: str, aPort: int = 80, aTimeOut: int = 1) -> bool:
    try:
        await asyncio.wait_for(asyncio.open_connection(aHost, aPort), timeout=aTimeOut)
        return True
    except: pass
