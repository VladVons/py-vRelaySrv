'''
Author:      Vladimir Vons, Oster Inc.
Created:     2022.03.29
License:     GNU, see LICENSE for more details
Description:
'''

import os
import re


class TProjFiles():
    def Run(self, aFile: str):
        with open(aFile, 'r') as F:
            Data = F.read()

        Find = re.findall('import\s+(.*)|from\s+(.*)\s+import\s+(.*)', Data)
        
        print(aFile, Find)
        for FindI in Find:
            for i in range(len(FindI)):
                Import = FindI[i]
                if (os.path.exists(Import)):
                    if (os.path.isdir(Import)):
                        FileInit = Import + '/__init__.py'
                        if (os.path.exists(FileInit)):
                            self.Run(FileInit)
                    else:
                        self.Run(Import)


os.system('clear')

PF = TProjFiles()
PF.Run('vRelaySrv.py')
