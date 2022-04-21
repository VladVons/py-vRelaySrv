import os
import asyncio
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


#------
import time
import multiprocessing
import threading
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver

#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager as Manager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager as Manager


#Opt = Options()
##Opt.add_argument("start-maximized")
#Drv = webdriver.Firefox(service=Service(Manager().install()), options=Opt)
#for i in range(10):
#    q1 = Drv.execute_script("window.open('');")
#    Drv.switch_to.window(Drv.window_handles[-1])
#    Drv.get('http://oster.com.ua')


class TSelenium():
    def __init__(self):
        #self.Init()
        pass

    def Init(self):
        Opt = Options()
        #Opt.add_argument("start-maximized")
        self.Drv = webdriver.Firefox(service=Service(Manager().install()), options=Opt)

    def __del__(self):
        #self.Drv.close()
        #self.Drv.quit()
        pass

    def Parse(self, aUrl: str):
        #https://www.youtube.com/watch?v=w7YEorllJZI
        #https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
        #https://chromedriver.storage.googleapis.com/index.html

        File = urlparse(aUrl).hostname
        print(File, os.getcwd())

        Opt = Options()
        #Opt.add_argument("start-maximized")
        self.Drv = webdriver.Firefox(service=Service(Manager().install()), options=Opt)

        try:
            self.Drv.get(aUrl)
            #Drv.implicitly_wait(3)
            time.sleep(1)
            self.Drv.save_screenshot(File + '.png')
            #p_element = Drv.find_element_by_id(id_='intro-text')
            #print(p_element.text)
        except Exception as E:
            print('Err', E)
        finally:
            self.Drv.close()
            self.Drv.quit()


    def Run(self, aUrls: list, aTask: int = 5):
        Pool = multiprocessing.Pool(processes=aTask)
        Pool.map(self.Parse, aUrls)
        Pool.close()
        Pool.join()

#asyncio.run(TestA_1())
#asyncio.run(Test_pyppeteer())
