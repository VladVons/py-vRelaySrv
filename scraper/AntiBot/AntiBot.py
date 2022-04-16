'''
https://github.com/Anorov/cloudflare-scrape
https://github.com/venomous/cloudscraper
https://github.com/Anorov/cloudflare-scrape#dependencies
'''

import os
import asyncio
from aiocfscrape import CloudflareScraper


class TUrl():
    async def Get_2(self, aUrl):
        Res = ''
        async with CloudflareScraper() as Session:
            async with Session.get(aUrl) as Response:
                Res = await Response.text()
                if (Response.status == 200):
                    return Res
        return ''

asyncio.run(TUrl().Get_2('https://itmag.ua'))


