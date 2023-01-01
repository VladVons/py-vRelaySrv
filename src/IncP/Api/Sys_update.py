'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.01.27
License:     GNU, see LICENSE for more details
Description:
'''


import json, os, uio
#
from App import ConfApp
from IncP.Log import Log
from Inc.Http.HttpUrl import UrlLoad
from IncP.Api import TApiBase


class TApi(TApiBase):
    @staticmethod
    async def DownloadList(aUrl: str) -> bool:
        Buf = uio.BytesIO()
        try:
            await UrlLoad(aUrl, Buf)
            Data = Buf.getvalue().decode('utf-8')
            Data = json.loads(Data)
            Buf.close()
        except Exception as E:
            Log.Print(1, 'x', 'DownloadList()', E)
            return False

        Size = 0
        Root = aUrl.rsplit('/', 1)[0]
        Files = Data.get('Files', [])
        for File in Files:
            Arr = File.rsplit('/', 1)
            if (len(Arr) == 2):
                try:
                    os.mkdir(Arr[0])
                except: pass

            Url = Root + '/' + File
            with open(File, 'w') as hFile:
                await UrlLoad(Url, hFile)
                hFile.seek(0, 2)
                Size += hFile.tell()
        return (Data.get('Size', 0) == Size)

    async def Exec(self, aUrl: str) -> dict:
        R = await TApi.DownloadList(aUrl)
        return {'result': R, 'alias': ConfApp.get('Alias'), 'hint': 'Reset ?'}

    async def Query(self, aData: dict) -> dict:
        Url = aData.get('url')
        return await self.Exec(Url)
        # ToDo. No output in Http. Possible double write to stream, close, etc 
