from ..Api import Api
from .FForm import TFormBase
from Inc.DB.DbList import TDbList, TDbCond
from IncP.Utils import GetNestedKey


class TForm(TFormBase):
    Title = 'Index'
    Pages = {
        '/form/soup_get': 'soup get',
        '/form/soup_make': 'soup make',
        '/form/soup_test': 'soup test',
        '/form/sites_list': 'sites list',
        '/form/sites_add': 'sites_add',
        '/form/site_get': 'site get',
        '/form/tools': 'tools',
    }

    async def _Render(self):
        self.Data.Pages = {
            Key: Val
            for Key, Val in self.Pages.items()
            if (self.CheckAccess(Key))
        }
