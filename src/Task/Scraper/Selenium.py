'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.21
License:     GNU, see LICENSE for more details

# protected url
https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
https://www.vindecoderz.com/EN/check-lookup/ZDMMADBMXHB001652

# firefox download driver
#from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import GeckoDriverManager as Manager
#Service(Manager().install())
#
# chrome driver
https://sites.google.com/chromium.org/driver/downloads
#
# chrome driver all
https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
#
#sudo apt install chromium-chromedriver
#pip3 install webdriver-manager


Urls = []
Starter = TStarter()
Starter.ThreadCreate(Urls, 5)
'''

import asyncio
import multiprocessing
import time

#from selenium.webdriver import Chrome as Browser
#from selenium.webdriver.chrome.options import Options

from selenium.webdriver.firefox.webdriver import WebDriver as Browser
from selenium.webdriver.firefox.options import Options


class TSelenium():
    def __init__(self, aParent):
        self.Parent = aParent

        Opt = Options()
        #Opt.add_argument('start-maximized')
        #Opt.add_argument('--headless')
        #Opt.add_argument('--disable-blink-features=AutomationControlled')
        self.Driver = Browser(options=Opt)

    def Close(self):
        self.Driver.close()
        self.Driver.quit()

    def Run(self, aQueue):
        while (self.Parent.IsRun.value) and (not aQueue.empty()):
            Url = aQueue.get()
            print('Run', Url)
            self.Driver.get(Url)
            time.sleep(2)
            aQueue.task_done()
        #print('Run end')


class TStarter():
    def __init__(self):
        self.IsRun = multiprocessing.Value('i')

    def ThreadRun(self, aQueue):
        Obj = TSelenium(self)
        try:
            Obj.Run(aQueue)
        finally:
            Obj.Close()
        #print('ThreadRun end')

    async def ThreadCreate(self, aUrls: list, aCnt: int = 1):
        self.IsRun.value = True

        Queue = multiprocessing.JoinableQueue()
        _NotUsed = [Queue.put(x) for x in aUrls]

        for _i in range(aCnt):
            process = multiprocessing.Process(target = self.ThreadRun, args = [Queue])
            process.daemon = True
            process.start()
            time.sleep(0.5)

        #--- sync wait
        #Queue.join()
        #time.sleep(3)

        #--- async wait
        while (not Queue.empty()):
            await asyncio.sleep(10)

        print('ThreadCreate end')
