"""
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2021.02.28
License:     GNU, see LICENSE for more details
Description:
"""

import traceback
#
from Inc.Log import TLog


class TLogEx(TLog):
    def DoExcept(self, aE):
        traceback.print_exc()

Log = TLogEx()
