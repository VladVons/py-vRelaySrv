import aiohttp_jinja2

class TFormBase():
    Title = 'Title'

    def __init__(self, aRequest, aTpl: str):
        self.Request = aRequest
        self.Tpl = aTpl

    async def PostToForm(self):
        Post = await self.Request.post()
        for Key, Val in Post.items():
            setattr(self, Key, Val.strip())
        return bool(Post)

    def _Render(self):
        return aiohttp_jinja2.render_template(self.Tpl, self.Request, {'Form': self})
