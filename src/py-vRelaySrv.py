'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:.
'''


import os
import asyncio
#
from Inc.Conf import Conf
from IncP.Log  import Log, TEchoFile
from Inc.Plugin import Plugin
#
#import App


async def Run():
    _, Name = os.path.split(__file__)
    FileLog = '/var/log/py-vRelaySrv/%s.log' % (Name)
    Log.AddEcho(TEchoFile(FileLog))
    print('Log file ' + FileLog)

    Log.Print(1, 'i', 'Run', os.uname())

    Plugin.LoadList(Conf.get('Plugins'))
    try:
        await Plugin.Run()
    except KeyboardInterrupt:
        Log.Print(1, 'x', 'Run()', 'Ctrl-C')
    finally:
        await Plugin.Stop()


if (Conf.Debug):
    event_loop = asyncio.get_event_loop()
    event_loop.set_debug(True)
    event_loop.slow_callback_duration = 0.001
    event_loop.run_until_complete(Run())
else:
    #event_loop = asyncio.get_event_loop()
    #event_loop.run_until_complete(Run())

    # >= 3.7
    asyncio.run(Run())
