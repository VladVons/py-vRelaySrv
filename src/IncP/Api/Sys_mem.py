'''
Author:      Vladimir Vons, Oster Inc.
Created:     2018.06.17
License:     GNU, see LICENSE for more details
Description:
'''


import gc


class TApi():
    async def Exec(self) -> dict:
        gc.collect()

        R = {
            'MemFree':  gc.mem_free(),
            'MemAlloc': gc.mem_alloc(),
        }
        return R

    async def Query(self, aData: dict) -> dict:
        return await self.Exec()
