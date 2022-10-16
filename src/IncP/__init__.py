'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.30
License:     GNU, see LICENSE for more details
'''


import os
import sys
import platform


__version__ = '1.0.24'
__date__ =  '2022.06.30'

def GetInfo() -> dict:
    UName =  platform.uname()
    Res = {
        'App' : os.path.basename(sys.argv[0]).rsplit('.')[0],
        'Descr': 'Web scraper',
        'Version' : __version__,
        'Date': __date__,
        'Author':  'Vladimir Vons',
        'eMail': 'VladVons@gmail.com',
        'HomePage': 'http://oster.com.ua',
        'OS': UName.system,
        'Host': UName.node,
        'User': os.environ.get('USER'),
        'Python': (sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
    }
    return Res
