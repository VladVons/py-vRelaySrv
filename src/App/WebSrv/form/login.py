'''
Copyright:   Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.16
License:     GNU, see LICENSE for more details
Description:
'''

from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from aiohttp import web
#
from IncP.Utils import GetNestedKey
from .FForm import TFormBase
from ..Api import Api


class TForm(TFormBase):
    Title = 'Login'

    UserName = StringField(validators = [DataRequired(), Length(min=1, max=32)], render_kw = {'placeholder': 'login'})
    Password = PasswordField(validators = [Length(min=1, max=16)], render_kw = {'placeholder': 'password'})
    Submit = SubmitField("ok")

    async def _Render(self):
        self.Message = self.Session.get('UserName')
        self.Query = self.Request.query_string
        if (self.validate()):
            Post = {'login': self.UserName.data, 'passw': self.Password.data}
            Data = await Api.WebClient.Send('web/get_user_id', Post)
            Id = GetNestedKey(Data, 'Data.Data')
            if (Id):
                self.Session['UserId'] = Id
                self.Session['UserName'] = self.UserName.data
                Redirect = self.Request.query.get('url')
                raise web.HTTPFound(location = Redirect)
            else:
                self.Message = 'Wrong authorization'
