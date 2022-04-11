import aiohttp_jinja2


class TDictStr(dict):
    def __getattr__(self, aName: str) -> object:
        return self.get(aName, '')


class TFormBase():
    Title = 'Title'

    def __init__(self, aRequest, aTpl: str):
        self.Request = aRequest
        self.Tpl = aTpl
        self.Data = TDictStr()

    async def PostToForm(self):
        Post = await self.Request.post()
        for Key, Val in Post.items():
            self.Data[Key] = Val.strip()
        return bool(Post)

    def _Render(self):
        return aiohttp_jinja2.render_template(self.Tpl, self.Request, {'Form': self.Data})
