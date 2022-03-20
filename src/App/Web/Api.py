'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.19
License:     GNU, see LICENSE for more details
Description:
'''

import json


class TApiTask():
    def __init__(self):
        self.Data = {}

    async def Get(self, aData: dict) -> dict:
        Res = await self.Parent.Db.GetUrlForUpdate()
        return Res


class TApi():
    Url = {
        'get_task':   {'param': []}
    }

    def __init__(self, aParent):
        self.Parent = aParent
        self.ApiTask = TApiTask()
        self.Cnt = 0

    @staticmethod
    def GetMethodName(aPath: str) -> str:
        return 'path_' + aPath.replace('/', '_')

    async def Call(self, aPath: str, aParam: str) -> dict:
        UrlInf = self.Url.get(aPath)
        if (UrlInf):
            MethodName = self.GetMethodName(aPath)
            Method = getattr(self, MethodName, None)
            if (Method):
                ParamInf = UrlInf.get('param')
                if (ParamInf):
                    Param = json.loads(aParam)
                else:
                    Param = {}
                Data = await Method(Param)
                Res = {'Data': Data}
                self.Cnt += 1
            else:
                Res = {'Error': 'unknown method %s' % (MethodName)}
        else:
            Res = {'Error': 'unknown url %s' % (aPath)}
        return Res

    async def path_get_task(self, aData: dict) -> dict:
        return await self.ApiTask.Get(aData)
