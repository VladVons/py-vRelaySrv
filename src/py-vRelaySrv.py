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


class TApp():
    def InitLog(self):
        _, Name = os.path.split(__file__)
        FileLog = '/var/log/py-vRelaySrv/%s.log' % (Name)
        try:
            with open(FileLog, 'a') as File:
                File.writable()
        except:
            FileLog = '%s.log' % (Name)
        Log.AddEcho(TEchoFile(FileLog))
        print('Log file ' + FileLog)

    async def Run(self):
        self.InitLog()
        Log.Print(1, 'i', 'Start', os.uname())

        Plugin.LoadList(Conf.get('Plugins'))
        try:
            await Plugin.Run()
        except KeyboardInterrupt:
            Log.Print(1, 'x', 'Run()', 'Ctrl-C')
        finally:
            await Plugin.StopAll()
        Log.Print(1, 'i', 'End')


Task = TApp().Run()
if (Conf.Debug):
    event_loop = asyncio.get_event_loop()
    event_loop.set_debug(True)
    event_loop.slow_callback_duration = 0.001
    event_loop.run_until_complete(Task)
else:
    #event_loop = asyncio.get_event_loop()
    #event_loop.run_until_complete(Task)

    # >= 3.7
    asyncio.run(Task)
