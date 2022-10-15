'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.26
License:     GNU, see LICENSE for more details
'''


import os
import sys
import platform
#
from Task import ConfApp
from Inc.Log  import TEchoFile
from Inc.PluginTask import Plugin
from IncP import Info
from IncP.Log import Log, TEchoConsoleEx


class TApp():
    def InitLog(self):
        Log.AddEcho(TEchoConsoleEx())

        _, Name = os.path.split(__file__)
        FileLog = '/var/log/py-vRelaySrv/%s.log' % (Name)
        if (not os.path.exists(FileLog)) or (not os.access(FileLog, os.W_OK)):
            FileLog = '%s.log' % (Name)
        Log.AddEcho(TEchoFile(FileLog))
        print('Log file ' + FileLog)

    async def Run(self):
        self.InitLog()

        UName =  platform.uname()
        About = {
            'OS': UName.system,
            'Host': UName.node,
            'User': os.environ.get('USER'),
            'PyVer': (sys.version_info.major, sys.version_info.minor),
            'AppVer': (Info.get('Version'), Info.get('Date'))
        }
        Log.Print(1, 'i', 'Run() %s' % About)

        Plugin.LoadList(ConfApp.get('Plugins'))
        try:
            await Plugin.Run()
        except KeyboardInterrupt as E:
            Log.Print(1, 'x', 'Run()', aE = E)
        finally:
            await Plugin.StopAll()
        Log.Print(1, 'i', 'End')
