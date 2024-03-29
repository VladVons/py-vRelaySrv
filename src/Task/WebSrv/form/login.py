# Created: 2022.05.16
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from aiohttp import web
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
#
from Inc.DbList import TDbListSafe
from Inc.Util.Obj import DeepGet
from Inc.Misc.Misc import FilterKeyErr
from IncP.Log import Log
from ..Api import Api
from ..Session import Session
from .FormBase import TFormBase


class TForm(TFormBase):
    Title = 'Login'

    UserName = StringField(validators = [DataRequired(), Length(min=1, max=32)], render_kw = {'placeholder': 'login'})
    Password = PasswordField(validators = [Length(min=1, max=16)], render_kw = {'placeholder': 'password'})
    Submit = SubmitField("ok")

    async def _Render(self):
        self.Data.message = '%s (%s)' % (Session.Data.get('user_name'), Session.Data.get('user_group', ''))
        self.Data.query = self.Request.query_string
        if (not self.validate()):
            return

        DataApi = await Api.DefHandler('get_hand_shake')
        Err = FilterKeyErr(DataApi)
        if (Err):
            return self.RenderInfo(Err)

        Data = {'login': self.UserName.data, 'passw': self.Password.data}
        DataApi = await Api.DefHandler('get_user_id', Data)
        Err = FilterKeyErr(DataApi)
        if (Err):
            Log.Print(1, 'e', 'Err: %s' % Err)
            return

        DblJ = DeepGet(DataApi, 'data.data')
        Dbl = TDbListSafe().Import(DblJ)
        if (Dbl.IsEmpty()):
            self.Data.message = 'Authorization failed for %s' % (self.UserName.data)
            return

        UserId = Dbl.Rec.GetField('id')
        Session.Data.update({'user_id': UserId, 'user_name': self.UserName.data, 'user_group': Dbl.Rec.GetField('auth_group_name')})
        await Session.UpdateUserConfig()

        Redirect = self.Request.query.get('url', '/')
        raise web.HTTPFound(location = Redirect)
