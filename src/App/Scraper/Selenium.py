'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.21
License:     GNU, see LICENSE for more details
Description:

# download driver
#from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import GeckoDriverManager as Manager
#Service(Manager().install())

Urls = []
Starter = TStarter()
Starter.ThreadCreate(Urls, 5)
'''


import asyncio
import time
import multiprocessing

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class TSelenium():
    def __init__(self, aParent):
        self.Parent = aParent

        Opt = Options()
        #Opt.add_argument('start-maximized')
        #Opt.add_argument('--headless')
        self.Driver = webdriver.Firefox(options=Opt)

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
    def ThreadRun(self, aQueue):
        Obj = TSelenium(self)
        try:
            Obj.Run(aQueue)
        finally:
            Obj.Close()
        #print('ThreadRun end')

    async def ThreadCreate(self, aUrls: list, aCnt: int = 1):
        self.IsRun = multiprocessing.Value('i')
        self.IsRun.value = True

        Queue = multiprocessing.JoinableQueue()
        [Queue.put(x) for x in aUrls]

        for i in range(aCnt):
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
