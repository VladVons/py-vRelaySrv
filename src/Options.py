#Debug = True
Descr = 'frozen'
Plugins = 'App.Mqtt App.Http App.Idle'
Mqtt_Host = 'vpn2.oster.com.ua'
#Mqtt_User = 'test1'
#Mqtt_Passw = 'test1'

Http_Port = '8080'

AuthDb = {
    'DRIVER': '{MariaDbSQL}',
    'SERVER': '10.10.1.1',
    'DATABASE': 'app_grafana7',
    'UID': 'grafana7',
    'PWD': 'graf20197'
}
