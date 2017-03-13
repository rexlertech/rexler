import json
import logging
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.db.models import Q
from channels import Group, Channel
from channels.sessions import channel_session
from channels.auth import (http_session_user, channel_session_user_from_http,
                           channel_session_user)
from dateSite.models.chat import Room, Message
from dateSite.models.client import (Client, ManagerClient, Picture, PhotoAlbum,
                            ClientCollectionAlbum)
from dateSite.models.purchase import Record, Purchase
from dateSite.models.service import SubService

log = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_connect(message):
    client = Client.objects.filter(clicode=message.user.pk)
    if client:
        update = client.update(clireplychannel=message.reply_channel)
        if update > 0:
            tclcode = client[0].tclcode.tclcode
            if tclcode == 3:
                girls = ManagerClient.objects.filter(
                    clicodemanager=message.user.pk)
                for g in girls:
                    if g.clicodegirl.cliactive:
                        girl = Client.objects.filter(
                                clicode=g.clicodegirl.clicode).update(
                                clireplychannel=message.reply_channel)
        else:
            log.debug("Problems updating client's replychannel %s",
                      message.user.pk)
            return
    else:
        log.debug("Don't found the user with id %s", message.user.pk)
        return


@channel_session_user
def ws_receive(message):
    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return

    if set(data.keys()) != set(
            ('clicodesent', 'clicoderecieved', 'mescontent', 'type')):
        log.debug("ws message unexpected format data=%s", data)
        return

    # Si el logueado es el manager
    cli_sen = Client.objects.get(clicode=message.user.pk)
    if cli_sen.tclcode.tclcode == 3:
        act_for_manager = ManagerClient.objects.filter(
                                clicodemanager=message.user.pk,
                                clicodegirl=int(data['clicodesent'])).exists()
        if act_for_manager is False:
            log.debug("Manager with code %s is trying to send "
                      "message with girl %s" % (
                       message.user.pk, data['clicodesent']))
            return
    else:
        if(message.user.pk != int(data['clicodesent'])):
            log.debug("Someone is trying to send a message without login %s",
                      data['clicodesent'])
            return

    # Verificamos si el cliente tiene creditos para enviar mensajes
    cli_sen = Client.objects.get(clicode=data['clicodesent'])
    cli_rec = Client.objects.get(clicode=data['clicoderecieved'])
    cantidadCreditos = Purchase.credits(cli_sen)
    if cantidadCreditos == 0:
        d = {}
        d["error"] = {
            'type': '1',
            'message': ("You don't have credits. <br />"
                        "Would you like to buy some, click here?")}
        message.reply_channel.send({"text": json.dumps(d)})
    else:
        tipo = data["type"]
        del data["type"]
        data['clicodesent'], data['clicoderecieved'] = cli_sen, cli_rec

        if tipo == "mensaje":
            room = Room.get_room(clicode1=cli_sen, clicode2=cli_rec,
                                 clicodesent=cli_sen)
            subservice = SubService.objects.get(suscode=1)
            # Si no ha comenzado la conversacion
            if room.roostartdatetime is None:
                startconversation = Message.objects.filter(
                                    roocode=room.roocode,
                                    clicoderecieved=cli_sen.clicode)
                if startconversation:
                    room.set_startdatetime()
                    room.set_enddatetime(both=True, clicode=1)
            else:  # Si ya comenzó la conversación
                seg = timezone.now() - room.roostartdatetime
                room.set_enddatetime(False, clicode=cli_sen.clicode)
                if seg.total_seconds() <= 300:
                    minute = int(seg.total_seconds() // 60)
                    if minute > 0:
                        # Cobrar a ambos clientes
                        debit = subservice.susquantitycredit * minute
                        # Primer cliente
                        if cli_sen.fracode is None:
                            credits = Purchase.credits(cli_sen)
                            debit = Record.record_chat(
                                            cli_sen, cli_rec, debit,
                                            credits, subservice, room)
                            if debit > 0:
                                cobrado = Purchase.debitCredits(cli_sen, debit)
                        # Segundo cliente
                        if cli_rec.fracode is None:
                            credits = Purchase.credits(cli_rec)
                            debit = Record.record_chat(
                                            cli_rec, cli_sen, debit, credits,
                                            subservice, room)
                            if debit > 0:
                                cobrado = Purchase.debitCredits(cli_rec, debit)
                else:
                    # Para el primer cliente
                    if room.clicode1.fracode is None:
                        if room.rooendclient1 is False:
                            seg = timezone.now() - room.rooendc1datetime

                            if seg.total_seconds() > 300:
                                seg = (
                                 room.rooendc1datetime - room.roostartdatetime)
                                minute = int(seg.total_seconds() // 60) + 5
                                room.set_end(room.clicode1.clicode)
                            else:
                                seg = (
                                 room.rooendc1datetime - room.roostartdatetime)
                                minute = int(seg.total_seconds() // 60)

                            debit = subservice.susquantitycredit * minute
                            credits = Purchase.credits(room.clicode1)
                            debit = Record.record_chat(room.clicode1,
                                                       room.clicode2,
                                                       debit,
                                                       credits,
                                                       subservice,
                                                       room)
                            if debit > 0:
                                cobrado = Purchase.debitCredits(
                                    room.clicode1, debit)
                    # Para el segundo cliente
                    if room.clicode2.fracode is None:
                        if room.rooendclient2 is False:
                            seg = timezone.now() - room.rooendc2datetime

                            if seg.total_seconds() > 300:
                                seg = (
                                 room.rooendc2datetime - room.roostartdatetime)
                                minute = int(seg.total_seconds() // 60) + 5
                                room.set_end(room.clicode2.clicode)
                            else:
                                seg = (
                                 room.rooendc2datetime - room.roostartdatetime)
                                minute = int(seg.total_seconds() // 60)

                            debit = subservice.susquantitycredit * minute
                            credits = Purchase.credits(room.clicode2)
                            debit = Record.record_chat(room.clicode2,
                                                       room.clicode1,
                                                       debit,
                                                       credits,
                                                       subservice,
                                                       room)
                            if debit > 0:
                                cobrado = Purchase.debitCredits(
                                    room.clicode2, debit)
            content = Message.set_message(data["mescontent"])
            if content != data["mescontent"]:
                data["mescontentoriginal"] = data["mescontent"]
                data["mescontent"] = content
            m = room.messages_room.create(**data).as_dict()
            # Obtenemos el cliente que recibe como diccionario
            r, s = cli_rec.as_dict(), cli_sen.as_dict()
            r["credits"] = Purchase.credits(cli_rec)
            s["credits"] = Purchase.credits(cli_sen)
            d = {}
            d["clienterec"], d["clientesen"], d["mensaje"] = r, s, m
            room.send_message_room(d)
        elif tipo == "sticker":
            room = Room.get_room(cli_sen, cli_rec, cli_sen)
            subservice = SubService.objects.get(suscode=2)
            # Es un cliente
            if cli_sen.fracode is None:
                subservice = SubService.objects.get(suscode=2)
                creditsbysticker = subservice.susquantitycredit
                if(cantidadCreditos >= creditsbysticker):
                    debit = Record.record_sticker(cli_sen, cli_rec,
                                                  creditsbysticker,
                                                  cantidadCreditos,
                                                  subservice, room)
                    cobrado = Purchase.debitCredits(cli_sen, debit)
                    m = room.messages_room.create(**data).as_dict()
                    # Obtenemos el cliente que recibe como diccionario
                    r, s = cli_rec.as_dict(), cli_sen.as_dict()
                    r["credits"] = Purchase.credits(cli_rec)
                    s["credits"] = Purchase.credits(cli_sen)
                    d = {}
                    d["clienterec"], d["clientesen"], d["mensaje"] = r, s, m
                    room.send_message_room(d)
                else:
                    d = {}
                    d["error"] = {
                        'type': '1',
                        'message': ("You don't have enough credits to send "
                                    "a sticker. <br />Would you like to buy "
                                    "some, click here?")}
                    message.reply_channel.send({"text": json.dumps(d)})
            else:
                m = room.messages_room.create(**data).as_dict()
                # Obtenemos el cliente que recibe como diccionario
                r, s = cli_rec.as_dict(), cli_sen.as_dict()
                r["credits"] = Purchase.credits(cli_rec)
                s["credits"] = Purchase.credits(cli_sen)
                d = {}
                d["clienterec"], d["clientesen"], d["mensaje"] = r, s, m
                room.send_message_room(d)


@channel_session
def ws_disconnect(message):
    pass


def send_message(room, client_rec, client_sen, data, message):
    pass


@channel_session_user_from_http
def alerts(message):
    pass
