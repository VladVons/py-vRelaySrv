'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.04.20
License:     GNU, see LICENSE for more details
Description:

import Inc.Colored as Cl
#
Cl.Print('End', Cl.cRed)
Colored = Cl.Formats([('Hello ', Cl.cRed), ('World !', Cl.cYellow)])
print(Colored)
'''


cRed = (255, 0, 0)
cGreen = (0, 255, 0)
cBlue = (0, 0, 255)
cYellow = (255, 255, 0)
cLime = (0, 255, 0)
cCyan = (0, 255, 255)
cMagenta = (255, 0, 255)
cGray = (128, 128, 128)
cSilver = (192, 192, 192)
cWhite = (255, 255, 255)
cDef = cSilver
#

def fg(aColor):
    return '\033[38;2;%sm' % (';'.join(str(x) for x in aColor))

def Format(aText: str, aColor: tuple = cWhite):
    return fg(aColor) + aText

def Print(aText: str, aColor: tuple = cWhite):
    print(fg(aColor) + aText + fg(cDef))
