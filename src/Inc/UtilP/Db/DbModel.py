import json
from psycopg2.errorcodes import UNIQUE_VIOLATION, NOT_NULL_VIOLATION
from psycopg2 import errors
#
from IncP.Log import Log
from .DbMeta import TDbMeta
from .ADb import TDbExecCurs


class TDbModel():
    def __init__(self, aDbMeta: TDbMeta, aPath: str):
        self.DbMeta = aDbMeta
        self.Conf = self._LoadJson(aPath + '/FConf.json')
        self.Master = self.Conf.get('master', '')

    @staticmethod
    def _TransDecor(aFunc):
        async def Wrapper(self, aData, *_aArgs):
            async with self.DbMeta.Db.Pool.acquire() as Connect:
                async with Connect.cursor() as Cursor:
                    Trans = await Cursor.begin()
                    try:
                        Res = await aFunc(self, aData, Cursor)
                    except (
                        errors.lookup(UNIQUE_VIOLATION),
                        errors.lookup(NOT_NULL_VIOLATION)
                    ) as E:
                        Res = {'err': str(E).split('\n', maxsplit = 1)[0]}
                        Log.Print(1, 'x', 'TransDecor()', aE=E, aSkipEcho=['TEchoDb'])

                    if (Res) and ('err' in Res):
                        #TransStat = await Connect.get_transaction_status()
                        #Res['trans'] = (TransStat != psycopg2.extensions.TRANSACTION_STATUS_INERROR)
                        await Trans.rollback()
                    else:
                        await Trans.commit()
                return Res
        return Wrapper

    def _LoadJson(self, aPath: str) -> dict:
        with open(aPath, 'r', encoding = 'utf8') as F:
            Res = json.load(F)
        return Res

    def _CheckConf(self, aData: dict) -> str:
        def Recurs(aData, aRequire: set) -> str:
            Res = ''
            if (isinstance(aData, list)):
                for x in aData:
                    Res = Recurs(x, aRequire)
                    if (Res):
                        break
            else:
                Diff = aRequire - set(aData.keys())
                if (Diff):
                    Res = f'required fields {Diff}'
            return Res

        ConfRequire = self.Conf.get('require', [])
        Diff = set(ConfRequire) - set(aData.keys())
        if (Diff):
            return f'require {Diff}'

        ConfAllow = self.Conf.get('allow', [])
        ConfDeny = self.Conf.get('deny', [])
        Depends = self.DbMeta.Foreign.TableId.get((self.Master, 'id'), {})
        for Table, Data in aData.items():
            if (self.Master) and (Table != self.Master):
                if (Depends) and (Table not in Depends):
                    return f'table {Table} not depends on {self.Master}'

            if (ConfAllow) and (Table not in ConfAllow):
                return f'table {Table} not allow'

            if (Table in ConfDeny):
                return f'table {Table} deny'

            Require = self.DbMeta.Table.Require.get(Table, []).copy()
            Depend = Depends.get(Table)
            if (Depend):
                Require.remove(Depend)
            Res = Recurs(Data, set(Require))
            if (Res):
                return f'table {Table} {Res}'

    async def _Add(self, aData: dict, aCursor = None) -> dict:
        Err = self._CheckConf(aData)
        if (Err):
            return {'err': Err}

        ResId = []
        if (self.Master):
            Dbl = await self.DbMeta.Insert(self.Master, aData.get(self.Master, {}), aReturning = ['id'], aCursor = aCursor)
            ResId = [self.Master, Dbl.Rec.GetField('id')]

        for Table, Data in aData.items():
            if (Table not in self.Master):
                ForeignVal = self.DbMeta.Foreign.GetColumnVal(Table, ResId)
                if (isinstance(Data, list)):
                    for x in Data:
                        await self.DbMeta.Insert(Table, x | ForeignVal, aCursor = aCursor)
                elif (isinstance(Data, dict)):
                    await self.DbMeta.Insert(Table, Data | ForeignVal, aCursor = aCursor)
        return {'id': ResId}

    async def _Del(self, aId: int, aCursor = None) -> dict:
        if (not await self.MasterHasId(aId, aCursor)):
            return {'err': f'id {aId} not found'}

        Depends = self.DbMeta.Foreign.TableId.get((self.Master, 'id'), {})
        for Table, Column in Depends.items():
            await self.DbMeta.Delete(Table, f'{Column} = {aId}', aCursor)
        await self.DbMeta.Delete(self.Master, f'id = {aId}', aCursor)

    @_TransDecor
    async def Add(self, aData: dict, aCursor = None) -> dict:
        return await self._Add(aData, aCursor)

    @_TransDecor
    async def AddList(self, aData: list, aCursor = None) -> list:
        Res = []
        for xData in aData:
            ResF = await self._Add(xData, aCursor)
            Res.append(ResF)
        return Res

    @_TransDecor
    async def Del(self, aId: int, aCursor = None) -> dict:
        return await self._Del(aId, aCursor)

    @_TransDecor
    async def DelList(self, aId: list[int], aCursor = None) -> list:
        Res = []
        for xId in aId:
            ResF = await self._Del(xId, aCursor)
            Res.append(ResF)
        return Res

    async def MasterHasId(self, aId: int, aCursor) -> bool:
        Query = f'select count(*) as count from {self.Master} where id = {aId}'
        Dbl = await TDbExecCurs(aCursor).Exec(Query)
        return Dbl.Rec.GetField('count') > 0
