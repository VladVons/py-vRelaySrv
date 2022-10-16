# -*- coding: utf-8 -*-

'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.26
License:     GNU, see LICENSE for more details
'''


import asyncio
from sys import version_info
#
from IncP import GetInfo
from Task.Main import TApp


def Run():
    Info = GetInfo()
    PyNeed = (3, 8, 0)
    if (Info['Python'] >= PyNeed):
        Task = TApp().Run()
        asyncio.run(Task)
    else:
        print(f'Need python >= {PyNeed}')

if (__name__ == '__main__'):
    Run()
