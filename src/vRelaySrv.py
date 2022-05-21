# -*- coding: utf-8 -*-

'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.26
License:     GNU, see LICENSE for more details
'''


import asyncio
import sys
#
from App import ConfApp
from App.Main import TApp

def Run():
    Task = TApp().Run()

    if (ConfApp.Debug):
        Loop = asyncio.get_event_loop()
        Loop.set_debug(True)
        Loop.slow_callback_duration = 0.01
        Loop.run_until_complete(Task)
    else:
        if (sys.version_info >= (3, 7)):
            asyncio.run(Task)
        else:
            Loop = asyncio.get_event_loop()
            Loop.run_until_complete(Task)

if (__name__ == '__main__'):
    Run()
