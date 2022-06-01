'''
https://github.com/Anorov/cloudflare-scrape
https://github.com/venomous/cloudscraper
https://github.com/Anorov/cloudflare-scrape#dependencies
'''

import os
import asyncio


def WriteFile(aFile: str, aData: str):
    with open(aFile, 'w') as F:
        Data = F.write(aData)

async def Get_2(aUrl):
    from aiocfscrape import CloudflareScraper

    async with CloudflareScraper() as Session:
        async with Session.get(aUrl) as Response:
            Res = await Response.text()
            if (Response.status == 200):
                WriteFile('Get_2.html', Res)


def Test2(aUrl):
    import cloudscraper

    scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
    Data = scraper.get(aUrl).text
    WriteFile('Test2.html', Data)

def Test3(aUrl):
   from debug import cfscrape
    scraper = cfscrape.create_scraper()
    Data = scraper.get(aUrl).content
    WriteFile('Test3.html', Data.decode())

Url = 'https://didi.ua'
#asyncio.run(Get_2(Url))
#Test2(Url)
Test3(Url)
