'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.14
License:     GNU, see LICENSE for more details
Description:
'''


try:
  import asyncio
except:
  import uasyncio as asyncio

import sys, select


class TKbdTerm():
    '''
    def __init__(self):
        self.Poller = select.poll()
        self.Poller.register(sys.stdin, select.POLLIN)
        pass

    #rst cause:4, boot mode:(3,6)
    def GetChr(self):
        for s, ev in self.Poller.poll(500):
            return s.read(1)
    '''

    def GetChr(self) -> str:
        R = ''
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            R = sys.stdin.read(1)
        return R


    async def Input(self, aPrompt = '') -> str:
        sys.stdout.write("%s%s   \r" % (aPrompt, ''))

        R = ''
        while True:
            K = self.GetChr()
            if (K):
                if (ord(K) == 10): # enter
                    print()
                    return R
                elif (ord(K) == 27): # esc
                    return ''
                elif (ord(K) == 127): # bs
                    R = R[:-1]
                else:
                    R += K
                sys.stdout.write("%s%s   \r" % (aPrompt, R))
            await asyncio.sleep(0.5)