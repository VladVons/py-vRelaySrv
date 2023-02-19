# Created: 2021.02.28
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from Inc.DbList import TDbListSafe
from Inc.Util.Obj import DeepGet
from Inc.Misc.Misc import FilterKeyErr
from IncP.ApiWeb import TApiBase
from IncP.ApiWeb import TWebClient
from IncP.Log import Log


class TApi(TApiBase):
    def __init__(self):
        super().__init__()

        self.DefMethod = self.DefHandler
        self.WebClient = TWebClient()

    async def DefHandler(self, aPath: str, aData: dict = None) -> dict:
        if (aData is None):
            aData = {}
        return await self.WebClient.Send('web/' + aPath, aData)

    async def GetUserConfig(self):
        User = self.WebClient.Auth.get('user')
        Data = {'login': User, 'passw': self.WebClient.Auth.get('password')}
        DataApi = await self.DefHandler('get_user_id', Data)
        Err = FilterKeyErr(DataApi)
        if (Err):
            Log.Print(1, 'e', 'Err: %s' % Err)
            return

        Dbl = TDbListSafe().Import(DeepGet(DataApi, 'data.data'))
        if (Dbl.IsEmpty()):
            Log.Print(1, 'e', 'GetUserConfig() failed for %s' % (User))
        else:
            UserId = Dbl.Rec.GetField('id')
            return await self.DefHandler('get_user_config', {'id': UserId})

    async def DoAuthRequest(self, aUser: str, aPassw: str) -> bool:
        return True


Api = TApi()
