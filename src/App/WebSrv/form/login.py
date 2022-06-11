'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.16
License:     GNU, see LICENSE for more details
'''

from aiohttp import web
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
#
from ..Api import Api
from .FForm import TFormBase
from Inc.DB.DbList import TDbList
from IncP.Utils import GetNestedKey


class TForm(TFormBase):
    Title = 'Login'

    UserName = StringField(validators = [DataRequired(), Length(min=1, max=32)], render_kw = {'placeholder': 'login'})
    Password = PasswordField(validators = [Length(min=1, max=16)], render_kw = {'placeholder': 'password'})
    Submit = SubmitField("ok")

    async def _Render(self):
        self.Message = self.Session.get('UserName')
        self.Query = self.Request.query_string
        if (not self.validate()):
            return

        DataApi = await Api.DefHandler('web/get_hand_shake')
        if (GetNestedKey(DataApi, 'Type') == 'Err'):
            return self.RenderInfo(DataApi.get('Data'))

        Post = {'login': self.UserName.data, 'passw': self.Password.data}
        DataApi = await Api.DefHandler('get_user_id', Post)
        Id = GetNestedKey(DataApi, 'Data.Data')
        if (Id):
            self.Session['UserId'] = Id
            self.Session['UserName'] = self.UserName.data

            DataApi = await Api.DefHandler('get_user_config', {'id': Id})
            DblJ = GetNestedKey(DataApi, 'Data.Data')
            if (DblJ):
                Conf = TDbList().Import(DblJ).ExportPair('name', 'data')
                self.Session['UserConf'] = Conf

            Redirect = self.Request.query.get('url', '/')
            raise web.HTTPFound(location = Redirect)
        else:
            self.Message = 'Authorization failed'
