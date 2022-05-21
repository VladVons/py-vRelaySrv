#https://docs.aiohttp.org/en/stable/web_advanced.html
#https://docs.aiohttp.org/en/stable/web.html

from aiohttp import web
import aiohttp_jinja2
#
from .form.info import TForm


Routes = web.RouteTableDef()

@Routes.post('/test2/{name}/q1')
@Routes.get ('/test2/{name}/q1')
async def rTest(aRequest: web.Request):
    #Data = await aRequest.post()
    Name = aRequest.match_info.get('name', '')
    Page = aRequest.rel_url.query.get('page', '')

    Context = {'name': 'pink_' + Name + ' + ' + Page}
    Response  = aiohttp_jinja2.render_template('about.tpl.html', aRequest, Context)
    return Response

async def rErr_404(aRequest: web.Request):
    Form = TForm(aRequest, 'info.tpl.html')
    Form.Data['Info'] = 'Page not found'
    return await Form.Render()

async def rErr_Def(aRequest: web.Request):
    return await rErr_404(aRequest)
