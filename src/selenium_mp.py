import time
import requests
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
import threading

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager as Manager

threadLocal = threading.local()

def GetUrls(aUrl: str) -> list:
  res = requests.get(aUrl)
  soup = BeautifulSoup(res.text, "lxml")
  hrefs = [x.get('href', '').strip().rstrip('/') for x in soup.find_all('a')]
  return list(set(hrefs))

def GetDriver():
  Res = getattr(threadLocal, 'Driver', None)
  if (Res is None):
      Opt = Options()
      #Opt.add_argument("start-maximized")
      Res = webdriver.Firefox(service=Service(Manager().install()), options=Opt)
      setattr(threadLocal, 'Driver', Res)
  return Res

def Parse(aUrl: str):
  Drv = GetDriver()
  print('--x1 ', aUrl)
  Drv.get(aUrl)
  time.sleep(3)

  #sauce = BeautifulSoup(driver.page_source, "lxml")
  #print(sauce)
  #item = sauce.select_one("h1 a").text
  #print(item)

class TColored():
    def Colored(aText: str, aColor: tuple = (255, 255, 255)):
        R, G, B = aColor
        return f"\033[38;2;{R};{G};{B}m{aText}\033[38;2;255;255;255m"


if __name__ == '__main__':
  #Url = 'http://oster.com.ua'
  Url = 'https://brain.com.ua'
  #links = GetUrls(Url)[:10]
  #ThreadPool(2).map(Parse, links)

  #from colored import fg
  #color = fg('blue')

  import Inc.Colored as Cl
  #Cl.Print('End', Cl.cRed)
  #Colored = Cl.Formats([('Hello ', Cl.cRed), ('World !', Cl.cYellow)])
  #print(Colored)
  print(Cl.fg(Cl.cRed) + 'Hello')
  print(Cl.Format('World', Cl.cBlue))
  Cl.Print('World', Cl.cYellow)




