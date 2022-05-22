import os
from Inc.Conf import TConf


ConfApp = TConf('Conf/App.py')
ConfApp.Load()
ConfApp.Def = {'Env_EmailPassw': os.getenv('Env_EmailPassw')}
