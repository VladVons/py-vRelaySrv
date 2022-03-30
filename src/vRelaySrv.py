'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:
'''


import os
import asyncio
#
from App import ConfApp
from App.Main import TApp


def Run():
    Task = TApp().Run()
    if (ConfApp.Debug):
        event_loop = asyncio.get_event_loop()
        event_loop.set_debug(True)
        event_loop.slow_callback_duration = 0.001
        event_loop.run_until_complete(Task)
    else:
        #event_loop = asyncio.get_event_loop()
        #event_loop.run_until_complete(Task)

        # >= 3.7
        asyncio.run(Task)

if (__name__ == '__main__'):
    Run()
