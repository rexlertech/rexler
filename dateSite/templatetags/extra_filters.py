from django import template

register = template.Library()


@register.filter(name='remaining_pics')
def remaining_pics(length, sub):
    pics = int(length) - int(sub)
    if(pics > 99):
        return 99
    return pics


@register.filter(name='endswith')
def endswith(value, endswith):
    return value.endswith(endswith)

@register.filter(name='origincode')
def origincode(lista):
    lon = len(lista) - 1
    value = lista[lon]["inbcodeorigin"]
    if value == None:
        value = lista[lon]["inbcode"]
    return value

@register.filter(name='otherclient')
def otherclient(lista,mainclient):
    lon = len(lista) - 1
    sender = lista[lon]["inbclicodesent"]
    if (sender == mainclient):
        sender = lista[lon]["inbclicoderecieved"]
    return sender;
