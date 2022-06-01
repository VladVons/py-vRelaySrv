'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
'''


from IncP.ApiWeb import TApiBase
from IncP.ApiWeb import TWebClient
from IncP.Log import Log
from IncP.Utils import GetNestedKey


class TApi(TApiBase):
    def __init__(self):
        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

    async def DefHandler(self, aPath: str, aData: dict = {}) -> dict:
        return await self.WebClient.Send('web/' + aPath, aData)

    async def GetUserConfig(self):
        Data = {'login': self.WebClient.Auth.get('User'), 'passw': self.WebClient.Auth.get('Password')}
        DataApi = await self.DefHandler('get_user_id', Data)
        if (DataApi):
            Data = {'id': GetNestedKey(DataApi, 'Data.Data')}
            return await self.DefHandler('get_user_config', Data)
        else:
            Log.Print(1, 'GetUserConfig() failed')

Api = TApi()
