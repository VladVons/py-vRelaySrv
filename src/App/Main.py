'''
Author:      Vladimir Vons, Oster Inc.
Created:     2021.02.26
License:     GNU, see LICENSE for more details
Description:
'''


import os, sys
#
from App import ConfApp
from Inc.Plugin import Plugin
from Inc.Log  import TEchoFile
from IncP.Log  import Log, TEchoConsoleEx
from IncP import Info


class TApp():
    def InitLog(self):
        Log.AddEcho(TEchoConsoleEx())

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

        UName = os.uname()
        About = {
            'OS': UName.sysname,
            'Host': UName.nodename,
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
