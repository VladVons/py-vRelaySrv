# -*- coding: utf-8 -*-

'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:
'''


import sys
import asyncio
#
from App import ConfApp
from App.Main import TApp


def Run():
    Task = TApp().Run()

    if (ConfApp.Debug):
        Loop = asyncio.get_event_loop()
        Loop.set_debug(True)
        Loop.slow_callback_duration = 0.001
        Loop.run_until_complete(Task)
    else:
        if (sys.version_info.minor >= 7):
            asyncio.run(Task)
        else:
            Loop = asyncio.get_event_loop()
            Loop.run_until_complete(Task)

if (__name__ == '__main__'):
    Run()
