# Created: 2021.02.26
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
#
from Task import ConfTask
from Inc.PluginTask import Plugin
from IncP import GetInfo
from IncP.Log import Log, TEchoConsoleEx, TEchoFileEx


class TTask():
    def __init__(self):
        self.Info = GetInfo()

    def InitLog(self):
        AppName = self.Info['App']
        FileLog = f'/var/log/{AppName}/{AppName}.log'
        if (not os.path.exists(FileLog)) or (not os.access(FileLog, os.W_OK)):
            FileLog = f'{AppName}.log'
        Log.AddEcho(TEchoFileEx(FileLog))
        print(f'Log file {FileLog}')

        Log.AddEcho(TEchoConsoleEx())

    async def Run(self):
        self.InitLog()

        Log.Print(1, 'i', 'Run() %s' % self.Info['App'])

        Plugin.LoadList(ConfTask.get('Plugins', ''))
        try:
            await Plugin.Run()
        except KeyboardInterrupt as E:
            Log.Print(1, 'x', 'TTask.Run()', aE = E)
        except Exception as E:
            Log.Print(1, 'x', 'TTask.Run()', aE = E)
            raise E
        finally:
            await Plugin.StopAll()
        Log.Print(1, 'i', 'End')
