import re
import json
from django.db import models
from django.utils import timezone
from django.db.models import Q, Max, Count
from channels import Group, Channel
from .client import Client, ManagerClient


class Room(models.Model):
    roocode = models.BigAutoField(primary_key=True)
    roostartdatetime = models.DateTimeField('Datetime to start chat',
                                            null=True, blank=True)
    rooendclient1 = models.BooleanField(default=False)
    rooendclient2 = models.BooleanField(default=False)
    rooendc1datetime = models.DateTimeField('Datetime to end chat client1',
                                            null=True, blank=True)
    rooendc2datetime = models.DateTimeField('Datetime to end chat client2',
                                            null=True, blank=True)
    clicode1 = models.ForeignKey(Client, models.DO_NOTHING,
                                 db_column='clicode1',
                                 related_name='room_client1')
    clicode2 = models.ForeignKey(Client, models.DO_NOTHING,
                                 db_column='clicode2',
                                 related_name='room_client2')

    def __unicode__(self):
        return self.roocode

    @property
    def websocket_group(self):
        return Group("room-%s-%s" % (self.clicode1.clicode,
                                     self.clicode2.clicode))

    def get_room(clicode1, clicode2, clicodesent):
        if clicode1.clicode > clicode2.clicode:
            aux = clicode1
            clicode1, clicode2 = clicode2, aux
        filtro = Q(clicode1=clicode1.clicode) & Q(clicode2=clicode2.clicode)
        room = Room.objects.filter(filtro).order_by("-roocode").first()
        if room:
            if room.roostartdatetime is None:
                get_room = room
            elif room.rooendclient1 is True & room.rooendclient2 is True:
                get_room = Room.create_room(clicode1, clicode2)
            else:
                if clicode1.clicode == clicodesent.clicode:
                    endclient = room.rooendclient1
                    seg = timezone.now() - room.rooendc1datetime
                elif clicode2.clicode == clicodesent.clicode:
                    endclient = room.rooendclient2
                    seg = timezone.now() - room.rooendc2datetime
                if endclient is True:
                    Room.objects.filter(roocode=room.roocode).update(
                        rooendclient1=True, rooendclient2=True)
                    get_room = Room.create_room(clicode1, clicode2)
                else:
                    if seg.total_seconds() <= 300:
                        get_room = room
                    else:
                        Room.objects.filter(roocode=room.roocode).update(
                            rooendclient1=True, rooendclient2=True)
                        get_room = Room.create_room(clicode1, clicode2)
        else:
            get_room = Room.create_room(clicode1, clicode2)
        return get_room

    def create_room(clicode1, clicode2):
        room = Room(clicode1=clicode1, clicode2=clicode2)
        room.save()
        return room

    def send_message_room(self, data):
        if self.rooendclient1 is True:
            gen = str(self.clicode1.gencode.gencode)
            if (gen == "2" or gen == "4"):
                gender = 'she'
            else:
                gender = 'he'
            data["error"] = {'type': '2',
                             'message': ('When @%s get into the room, '
                                         ' %s can see your messages') % (
                                 self.clicode1.cliusername,
                                 gender),
                             'title': '@%s left the room' % (
                                 self.clicode1.cliusername)}
            Channel(self.clicode2.clireplychannel).send({
                "text": json.dumps(data)
            })
        elif self.rooendclient2 is True:
            gen = str(self.clicode2.gencode.gencode)
            if (gen == "2" or gen == "4"):
                gender = 'she'
            else:
                gender = 'he'
            data["error"] = {'type': '2',
                             'message': ('When @%s get into the room, '
                                         ' %s can see your messages') % (
                                 self.clicode2.cliusername,
                                 gender),
                             'title': '@%s left the room' % (
                                 self.clicode2.cliusername)}
            Channel(self.clicode1.clireplychannel).send({
                "text": json.dumps(data)
            })
        elif (self.clicode1.clireplychannel is not None and
                self.clicode2.clireplychannel is not None):
            data["error"] = {'type': '0', 'message': ''}  # Perfect
            self.websocket_group.add(self.clicode1.clireplychannel)
            self.websocket_group.add(self.clicode2.clireplychannel)
            self.websocket_group.send({'text': json.dumps(data)})
        elif self.clicode1.clireplychannel:
            gen = str(self.clicode1.gencode.gencode)
            if (gen == "2" or gen == "4"):
                gender = 'she'
            else:
                gender = 'he'
            data["error"] = {'type': '2',
                             'message': 'When @%s connects, %s '
                                        'can see your messages' % (
                                            self.clicode2.cliusername,
                                            gender),
                             'title': '@%s is offline' % (
                                            self.clicode2.cliusername)}
            Channel(self.clicode1.clireplychannel).send({
                "text": json.dumps(data)
            })
        elif self.clicode2.clireplychannel:
            gen = str(self.clicode1.gencode.gencode)
            if (gen == "2" or gen == "4"):
                gender = 'she'
            else:
                gender = 'he'
            data["error"] = {'type': '2',
                             'message': 'When @%s connects, %s '
                                        'can see your messages' % (
                                            self.clicode1.cliusername,
                                            gender),
                             'title': '@%s is offline' % (
                                            self.clicode1.cliusername)}
            Channel(self.clicode2.clireplychannel).send({
                "text": json.dumps(data)
            })

    def set_startdatetime(self):
        Room.objects.filter(roocode=self.roocode).update(
            roostartdatetime=timezone.now())

    def set_end(self, clicode):
        if self.clicode1.clicode == clicode:
            Room.objects.filter(roocode=self.roocode).update(
                rooendclient1=True)
        elif self.clicode2.clicode == clicode:
            Room.objects.filter(roocode=self.roocode).update(
                rooendclient2=True)

    def set_enddatetime(self, both, clicode):
        if both:
            Room.objects.filter(roocode=self.roocode).update(
                rooendc1datetime=timezone.now(),
                rooendc2datetime=timezone.now())
        else:
            if self.clicode1.clicode == clicode:
                Room.objects.filter(roocode=self.roocode).update(
                    rooendc1datetime=timezone.now())
            elif self.clicode2.clicode == clicode:
                Room.objects.filter(roocode=self.roocode).update(
                    rooendc2datetime=timezone.now())

    def leave_page(clicode):
        client = Client.objects.filter(clicode=clicode)
        if client:
            if client.tclcode.tclcode == 3:  # Es una Manager
                girls = ManagerClient.objects.filter(clicodemanager=clicode)
                for g in girls:
                    code = g.clicodegirl.clicode
                    filtro = (Q(clicode1=code) | Q(clicode2=code))
                    filtro = filtro & (Q(rooendclient1=False)
                                       | Q(rooendclient2=False))
                    filtro = filtro & Q(roostartdatetime__isnull=False)
                    rooms = Room.objects.filter(filtro)
                    for r in rooms:
                        if (r.clicode1.clicode == code):
                            r.rooendclient1 = True
                        else:
                            r.rooendclient2 = True
                        r.save()
            else:
                filtro = (Q(clicode1=clicode) | Q(clicode2=clicode))
                filtro = filtro & (Q(rooendclient1=False) |
                                   Q(rooendclient2=False))
                filtro = filtro & Q(roostartdatetime__isnull=False)
                rooms = Room.objects.filter(filtro)
                for r in rooms:
                    if (r.clicode1.clicode == clicode):
                        r.rooendclient1 = True
                    else:
                        r.rooendclient2 = True
                    r.save()

    def getChatsRequest(clicode):
        filtro = Q(clicode1=clicode) | Q(clicode2=clicode)
        result = {}
        result["mychats"], result["myrequest"] = [], []
        roomsinvolved = Room.objects.filter(
            filtro).distinct('clicode1', 'clicode2')
        indChat, indReq = 0, 0
        mychats, myrequest = {}, {}
        for room in roomsinvolved:
            if (int(clicode) == int(room.clicode1.clicode)):
                recieved = room.clicode2.clicode
            else:
                recieved = room.clicode1.clicode

            lastRoom = Room.objects.filter(
                clicode1=room.clicode1.clicode,
                clicode2=room.clicode2.clicode).order_by(
                "roocode").last()
            messages = Message.objects.filter(
                roocode=lastRoom.roocode).order_by(
                "mescode").last()
            cantidad = Message.objects.filter(
                clicodesent=clicode,
                clicoderecieved=recieved).aggregate(
                cant=Count('roocode'))
            if(cantidad['cant'] > 0):  # mychat
                result["mychats"].append(messages.as_list(clicode=clicode))
            else:  # myrequest
                result["myrequest"].append(messages.as_list(clicode=clicode))

        return result

    class Meta:
        db_table = 'room'


class Message(models.Model):
    mescode = models.BigAutoField(primary_key=True)
    mescontent = models.TextField('Message')
    mescontentoriginal = models.TextField(
        'MessageOriginal', null=True, blank=True)
    mesdatetime = models.DateTimeField('Datetime to send message',
                                       default=timezone.now, db_index=True)
    mesread = models.BooleanField(default=False)
    roocode = models.ForeignKey(Room, models.DO_NOTHING,
                                db_column='roocode',
                                related_name='messages_room')
    clicodesent = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodesent',
                                    related_name='message_clientsent')
    clicoderecieved = models.ForeignKey(Client, models.DO_NOTHING,
                                        db_column='clicoderecieved',
                                        related_name='message_clientrecieved')

    def __unicode__(self):
        return ('[{mesdatetime}] {clicodesent} {clicoderecieved}:'
                '{mescontent}').format(**self.as_dict())

    @property
    def formatted_mesdatetime(self):
        return self.mesdatetime.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def mescontentshort(self):
        original = self.mescontent
        messhortcontent = ''

        i = 0
        inicio = []
        fin = []
        while(original.find("<img", i) > -1):
            i = original.find("<img", i)
            f = original.find(">", i) + 1
            inicio.append(i)
            fin.append(f)
            i = f
        lon = len(inicio)
        if (lon > 0):
            arr = []
            if (inicio[0] != 0):  # es texto
                arr.append(original[0:inicio[0]])
            for i in range(lon):
                if i > 0:
                    indexfin = fin[i - 1]
                    indexinicio = inicio[i]
                    if (indexfin != indexinicio):  # es texto
                        arr.append(original[indexfin:indexinicio])
                arr.append(original[inicio[i]:fin[i]])  # es imagen
            indexend = len(original) - 1
            if (fin[lon - 1] < indexend):  # es texto
                arr.append(original[fin[lon - 1]:])
            meslon = 0
            for i in range(len(arr)):
                if (arr[i][0] == "<"):
                    lonnewtext = 5
                    img = True
                else:
                    lonnewtext = len(arr[i])
                    img = False
                if((meslon + lonnewtext) > 30):
                    if(img is False):
                        quedan = 30 - meslon
                        messhortcontent = messhortcontent + arr[i][:quedan]
                    break
                else:
                    meslon = meslon + lonnewtext
                    messhortcontent = messhortcontent + arr[i]
        else:
            messhortcontent = original[0:40]
        return messhortcontent

    def set_message(content):
        position = content.find("@")
        if position >= 0:
            content = content.partition("@")[0] + "*********"
        arr = content.split(" ")
        lista = ['arroba', 'arrova', 'aroba', 'arova', 'give money',
                 'give me money', 'tarjeta', 'credit card', 'money',
                 'email', 'mail', 'email address', 'facebook', 'fb',
                 'instagram', 'phone', 'cc', 'phone number', 'twitter', 'tw',
                 'western union', 'money gram', 'http', 'gmail', 'hotmail',
                 '.com', 'doctor', 'payment', 'medical', 'target']
        lista_temp = []
        for a in arr:
            encontrado = False
            for x in lista:
                if a == x:
                    encontrado = True
                    arr.remove(a)
                    break
            if encontrado is True:
                lista_temp.append("**")
            else:
                lista_temp.append(a)
        content = ""
        for a in lista_temp:
            if content == "":
                content = a
            else:
                content = "%s %s" % (content, a)
        return content

    def quantityNotRead(clicode):
        total = Message.objects.filter(
            clicoderecieved=clicode, mesread=False).count()
        return total

    def as_dict(self):
        return {
            'mescode': self.mescode,
            'clicodesent': self.clicodesent.clicode,
            'clicoderecieved': self.clicoderecieved.clicode,
            'mescontent': self.mescontent,
            'mesdatetime': self.formatted_mesdatetime,
            'mescontentshort': self.mescontentshort
        }

    def as_list(self, clicode=0):
        msg_list = {
            'sentcode': self.clicodesent.clicode,
            'sentprofilepicture': self.clicodesent.profile_picture,
            'sentusername': self.clicodesent.cliusername,
            'sentage': self.clicodesent.age,
            'mescontent': self.mescontentshort,
            'recievedcode': self.clicoderecieved.clicode,
            'recievedprofilepicture': self.clicoderecieved.profile_picture,
            'recievedusername': self.clicoderecieved.cliusername,
            'recievedage': self.clicoderecieved.age,
        }
        if int(clicode) > 0:
            msg_list['msg_qty'] = Message.objects.filter(
                clicoderecieved=clicode,
                mesread=False,
                roocode=self.roocode.roocode).count()
        return msg_list

    class Meta:
        db_table = 'message'
