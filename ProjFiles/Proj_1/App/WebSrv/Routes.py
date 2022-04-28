#https://docs.aiohttp.org/en/stable/web_advanced.html
#https://docs.aiohttp.org/en/stable/web.html

import aiohttp_jinja2
from aiohttp import web
#
from .form.err_404 import TForm


Routes = web.RouteTableDef()

@Routes.post('/test2/{name}/q1')
@Routes.get ('/test2/{name}/q1')
async def rTest(aRequest):
    #Data = await aRequest.post()
    Name = aRequest.match_info.get('name', '')
    Page = aRequest.rel_url.query.get("page", '')

    Context = {'name': 'pink_' + Name + ' + ' + Page}
    Response  = aiohttp_jinja2.render_template('about.tpl.html', aRequest, Context)
    return Response

async def rErr_404(aRequest):
    Form = TForm(aRequest, 'err_404.tpl.html')
    return await Form.Render()

async def rErr_Def(aRequest):
    return await rErr_404(aRequest)
