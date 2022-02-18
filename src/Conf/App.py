#Debug = True
Descr = 'frozen'
Plugins = 'App.Mqtt App.Http App.Idle'
#

#Mqtt_Host = 'localhost'
Mqtt_Host = '192.168.2.115'
#Mqtt_User = 'test1'
#Mqtt_Passw = 'test1'
#
Http_Port = '8080'

#
#AuthDbOdbc = {
#    'DRIVER': '{MariaDbSQL}',
#    'SERVER': '10.10.1.1',
#    'DATABASE': 'app_vRelay_1',
#    'UID': 'vRelay',
#    'PWD': 'vR2021'
#}
#

#AuthDbMySql = {
#    'SERVER': 'localhost',
#    'DATABASE': 'app_vRelay_1',
#    'USER': 'vRelay',
#    'PASSWORD': 'vR2021'
#}

AuthDbMySql = {
    'SERVER': '192.168.2.115',
    'DATABASE': 'app_vRelay_2',
    'USER': 'vRelay',
    'PASSWORD': 'vR2021'
}
