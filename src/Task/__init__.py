import os
from Inc.Conf import TConf


ConfTask = TConf('Conf/Task.py')
ConfTask.Load()
ConfTask.Def = {'Env_EmailPassw': os.getenv('Env_EmailPassw')}
