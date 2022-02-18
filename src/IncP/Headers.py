import random


class THeaders():
    def __init__(self):
        self.OS = ['Macintosh; Intel Mac OS X 10_15_5', 'Windows NT 10.0; Win64; x64; rv:77', 'Linux; Intel Ubuntu 20.04']
        self.Browser = ['Chrome/83', 'Firefox/77', 'Opera/45']

    def Get(self):
        OS = self.OS[random.randint(0, len(self.OS) - 1)]
        Browser = self.Browser[random.randint(0, len(self.Browser)) - 1]
        return {
            'Accept': '*/*',
            'User-Agent': 'XMozilla/5.0 (%s) %s' % (OS, Browser)
        }
