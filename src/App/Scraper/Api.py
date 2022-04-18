'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
'''


from IncP.Api import TApiBase


class TApi(TApiBase):
    async def GetConfig(self):
        Data = {'user': self.Auth.get('User')}
        return await self._Send('get_config', Data)

    async def GetTask(self):
        return await self._Send('get_task')

    async def SendResult(self, aData: dict):
        return await self._Send('send_result', aData)

Api = TApi()
