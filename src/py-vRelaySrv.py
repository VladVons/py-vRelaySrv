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


async def Run():
    Root, Name = os.path.split(__file__)
    FileLog = '/var/log/py-vRelaySrv/%s.log' % (Name)
    Log.AddEcho(TEchoFile(FileLog))
    print('Log file ' + FileLog)

    Log.Print(1, 'i', 'Run', os.uname())

    Plugin.LoadList(Conf.get('Plugins'))
    try:
        await Plugin.Run()
    except KeyboardInterrupt:
        Log.Print(1, 'i', 'Run()', 'Ctrl-C')
    finally:
        await Plugin.Stop()


asyncio.run(Run())
