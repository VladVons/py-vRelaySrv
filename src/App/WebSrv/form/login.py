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
from IncP.Log import Log
from IncP.Utils import GetNestedKey, FilterKeyErr


class TForm(TFormBase):
    Title = 'Login'

    UserName = StringField(validators = [DataRequired(), Length(min=1, max=32)], render_kw = {'placeholder': 'login'})
    Password = PasswordField(validators = [Length(min=1, max=16)], render_kw = {'placeholder': 'password'})
    Submit = SubmitField("ok")

    async def _Render(self):
        self.Message = '%s %s' % (self.Session.get('UserName'), self.Session.get('UserGroup', ''))
        self.Query = self.Request.query_string
        if (not self.validate()):
            return

        DataApi = await Api.DefHandler('get_hand_shake')
        if (GetNestedKey(DataApi, 'Type') == 'Err'):
            return self.RenderInfo(DataApi.get('Data'))

        Data = {'login': self.UserName.data, 'passw': self.Password.data}
        DataApi = await Api.DefHandler('get_user_id', Data)
        Err = FilterKeyErr(DataApi)
        if (Err):
            Log.Print(1, 'e', 'Err: %s' % Err)
            return

        Dbl = TDbList().Import(GetNestedKey(DataApi, 'Data.Data'))
        if (Dbl.IsEmpty()):
            self.Message = 'Authorization failed for %s' % (self.UserName.data)
            return

        UserId = Dbl.Rec.GetField('id')
        self.Session['UserId'] = UserId
        self.Session['UserName'] = self.UserName.data
        self.Session['UserGroup'] = Dbl.Rec.GetField('auth_group_name')

        DataApi = await Api.DefHandler('get_user_config', {'id': UserId})
        DblJ = GetNestedKey(DataApi, 'Data.Data')
        if (DblJ):
            Conf = TDbList().Import(DblJ).ExportPair('name', 'data')
            self.Session['UserConf'] = Conf

        Redirect = self.Request.query.get('url', '/')
        raise web.HTTPFound(location = Redirect)
