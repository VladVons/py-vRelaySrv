#https://docs.aiohttp.org/en/stable/web_advanced.html
#https://docs.aiohttp.org/en/stable/web.html

import aiohttp_jinja2
from aiohttp import web


Routes = web.RouteTableDef()

@Routes.post('/test2/{name}/q1')
@Routes.get ('/test2/{name}/q1')
async def rTest(aRequest):
        #Data = await aRequest.post()
        Name = aRequest.match_info.get('name', '')
        Page = aRequest.rel_url.query.get("page", '')

        Context = {'name': 'pink_' + Name + ' + ' + Page}
        Response  = aiohttp_jinja2.render_template('about.tpl', aRequest, Context)
        return Response

async def rError_404(aRequest):
    from .form.not_found import TForm
    Form = TForm(aRequest, 'not_found.tpl')
    return Form.Render()
