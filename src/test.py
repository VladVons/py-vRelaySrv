import os
import asyncio
import time
from Inc.Conf import TConf
#
#import cfscrape
#import cloudscraper

DbAuth = {
    'Server': 'localhost',
    'Database': 'test1',
    'User': 'postgres',
    'Password': '19710819'
}

async def TestA_1():
    DbApp = TDbApp(DbAuth)
    await DbApp.Connect()

    #Db1A = await DbApp.GetSitesForUpdate()
    #Db1A.Shuffle()
    #SiteId = Db1A.Rec.GetByName('site.id')

    #Db1 = await DbApp.GetSiteUrlsForUpdate(SiteId)
    #Db1 = await DbApp.GetSiteUrlsForUpdate(3)


    #q1 = await DbApp.GetTableColumns('scraper')
    #print(q1, type(q1), type(q1[0]))
    #return

    Db1 = await DbApp.GetScraper(1)

    await DbApp.Close()

    if (Db1.GetSize() > 0):
        #print()
        #print(Db1.Rec.Head)
        for Idx, Val in enumerate(Db1):
            #print(Idx, Val.Rec.GetByName('site.url'))
            #print(Val.Rec)
            print(Val.Rec.GetAsDict())

async def Test_pyppeteer():
    from pyppeteer import launch

    Url = 'http://oster.com.ua'
    browser = await launch()
    page = await browser.newPage()
    await page.setJavaScriptEnabled(True)
    await page.goto(Url)
    await page.screenshot({'path': 'example.png'})
    page_text = await page.content()
    await browser.close()
 

def Test_selenium():
    #https://www.youtube.com/watch?v=w7YEorllJZI
    #https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
    #https://chromedriver.storage.googleapis.com/index.html

    from bs4 import BeautifulSoup
    from selenium import webdriver
    import folium

    #from selenium.webdriver.chrome.service import Service
    #from selenium.webdriver.chrome.options import Options
    #from webdriver_manager.chrome import ChromeDriverManager as Manager
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from webdriver_manager.firefox import GeckoDriverManager as Manager

    #Url = 'https://www.google.com/search?client=ubuntu&hs=rJR&tbs=lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:10&tbm=lcl&sxsrf=APq-WBu7yNAUi-vRshMXWBsrRR0UFQ80Tg:1650352508976&q=%D0%BA%D0%BE%D0%BC%D0%BF%27%D1%8E%D1%82%D0%B5%D1%80%D0%B8%20%D1%82%D0%B5%D1%80%D0%BD%D0%BE%D0%BF%D1%96%D0%BB%D1%8C&rflfq=1&num=10&rlst=f#rlfi=hd:;si:;mv:[[49.5706392,25.652589199999998],[49.533133899999996,25.558039299999997]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:10'
    Url = 'http://oster.com.ua'

    Opt = Options()
    #Opt.add_argument("start-maximized")
    Drv = webdriver.Firefox(service=Service(Manager().install()), options=Opt)

    try:
        Drv.get(Url)
        Drv.save_screenshot('test.png')
        #p_element = Drv.find_element_by_id(id_='intro-text')
        #print(p_element.text)
        Drv.implicitly_wait(3)
    except Exception as E:
        print('Err', E)
    finally:
        Drv.close()
        Drv.quit()


#asyncio.run(TestA_1())
#asyncio.run(Test_pyppeteer())
Test_selenium()

