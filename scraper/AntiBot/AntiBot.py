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
                return Res
    return ''



def Test2(aUrl):
    import cloudscraper

    scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
    Data = scraper.get(aUrl).text
    return Data 

def Test3(aUrl):
    import cfscrape
    scraper = cfscrape.create_scraper()
    Data = scraper.get(aUrl).content
    return Data.decode() 

Url = 'https://didi.ua'
#Data = asyncio.run(Get_2(Url))
#Data = Test2(UrlUrl)
Data = Test3(Url)
WriteFile('Test2.html', Data)
