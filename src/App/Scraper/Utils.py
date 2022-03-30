"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.03.29
License:     GNU, see LICENSE for more details
Description:
"""
    

import re
import gzip
from IncP.Download import TDownload


'''
from IncP.Download import TDownload
LoadSiteMap(TDownload().Get, 'https://comtrade.ua/sitemap.xml')
'''
async def LoadSiteMap(aGetter, aUrl: str) -> list:
    Res = []

    Info = await aGetter(aUrl)
    if (Info):
        Data, Status = Info
        if (Status == 200):
            if (aUrl.endswith('.xml.gz')):
                Data = gzip.decompress(Data)

        Urls = re.findall('<loc>(.*?)</loc>', Data.decode())
        for Url in Urls:
            if (Url.endswith('.xml')) or (Url.endswith('.xml.gz')):
                Res += await LoadSiteMap(aGetter, Url)
            else:
                Res.append(Url.strip('/'))
    return Res
