# Created: 2022.10.19
# Author:  Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import sys
import traceback
from aiohttp import web


def CreateErroMiddleware(aOverrides):
    @web.middleware
    async def ErroMiddleware(request: web.Request, handler):
        try:
            return await handler(request)
        except web.HTTPException as E:
            Override = aOverrides.get(E.status)
            if (Override):
                return await Override(request)
            raise E
        except Exception as E:
            cwd = os.getcwd() + '/'
            Arr = traceback.format_exception(*sys.exc_info())
            Arr.insert(0, f'<b>{E}</b><br>')
            Arr = [x.replace(cwd, '') for x in Arr]
            Text = '\n<br>'.join(Arr)
            return web.Response(text = Text, content_type = 'text/html', status = 403)
    return ErroMiddleware
