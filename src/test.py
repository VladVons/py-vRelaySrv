#Arr = [1,2,3]

#print(','.join('"%s"' %A for A in Arr))
#print(str(Arr)[1:-1])


name = 'pink'
errno = 123

Str = 'Hey %(name)s, there is a 0x%(errno)d error!' % {"name": name, "errno": errno}
print(Str)

Str = 'Hey {name}, there is a {errno} error!'.format(name=name, errno=errno)
print(Str)
