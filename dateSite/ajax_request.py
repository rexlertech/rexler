import json
import random
import imghdr
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from .context_processor import *
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q

from dateutil.relativedelta import relativedelta

from .models.client import (Client, Picture, PhotoAlbum, ManagerClient,
                            ClientCollectionAlbum)
from .models.catalog import Gender, Feeling, City, Country, Language
from .models.notification import Notification, NotificationType
from .models.purchase import Record, Purchase
from .models.chat import Room
from .forms import UploadFilesForm

from .base_helper import (ExtJsonSerializer, convert_data_to_serielize)
from .models.credits import purch_album
from channels import Channel

from django_file_form.models import UploadedFile
from django.core.files import File


def ajax_feeling(request):
    if Client.objects.filter(clicode=request.user.pk).exists():
        feecode = request.POST.get('feeling')
        clicodesender = request.POST.get('sender')
        client = Client.objects.get(clicode=request.user.pk)
        # 3 es un manager
        if ((clicodesender != 0) & (client.tclcode.tclcode == 3)):
            client = Client.objects.get(clicode=clicodesender)

        if request.method == 'POST':
            client.feecode = Feeling.objects.get(feecode=feecode)
            client.save()
        return JsonResponse(feecode, safe=False)

    return JsonResponse({'error': True}, safe=False)


def ajax_info_complete_client(request):
    user = request.user
    girl = request.POST.get('girl')
    error = ""

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == 3:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to send message "
                              "with girl %s", (user.pk, girl))
                    error = ("You don't have permission to get this kind of "
                             "information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = 'Not results to show'

    if error != "":
        return JsonResponse({'error': error}, safe=False)
    else:
        data = client.client_complete()
        return JsonResponse(data, safe=False)

def ajax_qtynoti(request):
    clicode = request.POST.get('clicode')
    notis = Notification.quantityNotRead(clicode=clicode)
    data = {'qty': notis}
    return JsonResponse(data)


def ajax_readnoti(request):
    user = request.user
    q = int(request.POST.get('quantity'))
    error = ""
    code = request.user.pk

    # "girl" significa que es un manager
    if 'girl' in request.POST:
        girl = request.POST.get('girl')
        code = int(girl)
        exits = Client.objects.filter(clicode=user.pk).exists()
        if exits:
            client = Client.objects.get(clicode=user.pk)
            if client.cliactive:
                if client.tclcode.tclcode == 3:
                    act_for_manager = ManagerClient.objects.filter(
                        clicodemanager=user.pk,
                        clicodegirl=int(girl)).exists()
                    if act_for_manager is False:
                        log.debug("Manager with code %s is trying to update "
                                  "notifications from girl %s",
                                  (user.pk, girl))
                        error = ("You don't have permission to get this kind "
                                 "of information")
                    else:
                        client = Client.objects.get(clicode=int(girl))
                        if client.cliactive is False:
                            error = ("Client that you want to get information "
                                     "isn't active")
                else:
                    log.debug("Trying to update notification and not is a "
                              "manager %s.", user.pk)
                    error = "You can't get information"
            else:
                log.debug("Trying to update notification with inactive user "
                          "code %s.", user.pk)
                error = "You aren't active"
        else:
            log.debug("Trying to update notification with user code %s.",
                      user.pk)
            error = 'You are not a user'

    if error:
        data = {'error': 'yes', 'description': error}
    else:
        notis = Notification.objects.filter(
            clicoderecieved=code,
            notread=False).order_by(
            '-notcode')
        if notis:
            i = q
            for n in notis:
                n.notread = True
                n.save()
                i = i - 1
                if i <= 0:
                    break
        qty = Notification.quantityNotRead(clicode=code)
        data = {'error': 'no', 'qty': qty}
    return JsonResponse(data)


def ajax_check_readmessage(request):
    code = request.POST.get('code')
    if code:
        up = Message.objects.filter(mescode=code).update(mesread=True)
    return JsonResponse({'transaccion': 'ok'})


def ajax_clients(request):
    user = request.user
    min_age = request.POST.get('min_age')
    max_age = request.POST.get('max_age')
    country = request.POST.get('country')
    list_id = request.POST.get('list_id')

    members = get_client_list(user, min_age, max_age, country, list_id)

    if not members:
        return JsonResponse({'error': 'No results to show'}, safe=False)
    else:
        json_members = ExtJsonSerializer().serialize(
            members,
            default=convert_data_to_serielize,
            fields=['cliusername', 'cliname', 'age',
                    'clidescription', 'clibirthdate', 'citcode',
                    'marcode', 'educode', 'feecode', 'heicode',
                    'weicode', 'ocucode', 'ethcode', 'profile_picture',
                    'client_gallery'],
            indent=2,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True)
        return JsonResponse(json_members, safe=False)

    user = request.user
    girl = request.POST.get('girl')
    error = ""
    notifications = []

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == 3:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to get "
                              "notification with girl %s",
                              (user.pk, girl))
                    error = ("You don't have permission to get this kind "
                             "of information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = 'Not results to show'

    if error == "":
        i = 0
        exists = Notification.objects.filter(
            clicoderecieved=int(girl),
            notread=False).exists()
        if exists:
            noti = Notification.objects.filter(
                clicoderecieved=int(girl),
                notread=False)
            for n in noti:
                noti_detail = {}
                if n.ntycode.ntyactive:
                    noti_detail['notdescription'] = "@%s %s" % (
                        n.clicodesent.cliusername,
                        n.ntycode.ntydescription
                    )
                    noti_detail['notpicture'] = n.clicodesent.profile_picture
                    noti_detail['notdate'] = n.notdate
                    notifications.append(noti_detail)
                    i = i + 1
                    if i > 4:
                        break
        return JsonResponse(notifications, safe=False)
    else:
        return JsonResponse({'error': error}, safe=False)


def ajax_list_chat(request):
    user = request.user
    girl = request.POST.get('girl')
    error = ""

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == 3:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to get "
                              "notification with girl %s",
                              (user.pk, girl))
                    error = ("You don't have permission to get this kind "
                             "of information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = "Not results to show"

    if error == "":
        result = Room.getChatsRequest(girl)
        context = {}
        context['mychats'], context['myrequest'] = [], []
        if len(result) > 0:
            if "mychats" in result:
                if len(result["mychats"]) > 0:
                    context['mychats'].append(result["mychats"])
            if "myrequest" in result:
                if len(result["myrequest"]) > 0:
                    context['myrequest'].append(result["myrequest"])
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse({'error': error}, safe=False)


def ajax_profile_picture(request):
    picture = request.POST.get('picture_id')

    client_albums = PhotoAlbum.objects.filter(
        clicode=request.user.pk).exclude(phatype=2)
    pictures = Picture.objects.filter(
        phacode__in=client_albums).update(
        picprofile=False)
    new_picture = Picture.objects.filter(piccode=picture).first()
    new_picture.picprofile = True
    new_picture.save()

    picture = str(new_picture.picpath)
    albumid = str(new_picture.phacode_id)
    album = str(new_picture.phacode.phaname)

    return JsonResponse({'pic': picture,
                         'albumid': albumid,
                         'album': album}, safe=False)


def ajax_get_album(request):
    albumid = request.POST.get('albumid')

    album = PhotoAlbum.objects.filter(phacode=albumid)
    albums = get_client_albums(Client.objects.get(
                               clicode=request.user.pk),
                               album)

    return JsonResponse(albums, safe=False)


def ajax_get_albums(request):
    albums = get_client_albums(Client.objects.get(
                               clicode=request.user.pk))
    return JsonResponse(albums, safe=False)


def ajax_add_private_album(request):
    album_added = request.POST.get('album_id')

    response = purch_album(request, album_added)

    return JsonResponse(response, safe=False)

def ajax_delete_album(request):
    albumid = request.POST.get('album_id')
    album = PhotoAlbum.objects.get(phacode=albumid)
    Picture.objects.filter(phacode=album.phacode).update(picactive=False)
    album.phaactive = False
    album.save()

    return JsonResponse({'message': 'Album deleted'}, safe=False)

def ajax_clients(request):
    user = request.user
    error = ""
    # "girl" significa que es un manager
    if 'girl' in request.POST:
        girl = request.POST.get('girl')
        code = int(girl)
        exits = Client.objects.filter(clicode=user.pk).exists()
        if exits:
            client = Client.objects.get(clicode=user.pk)
            if client.cliactive:
                if client.tclcode.tclcode == 3:
                    act_for_manager = ManagerClient.objects.filter(
                        clicodemanager=user.pk,
                        clicodegirl=int(girl)).exists()
                    if act_for_manager is False:
                        log.debug("Manager with code %s is trying to get a "
                                  "client list from girl %s",
                                  (user.pk, girl))
                        error = ("You don't have permission to get this kind "
                                 "of information")
                    else:
                        client = Client.objects.get(clicode=int(girl))
                        if client.cliactive is False:
                            error = ("Client that you want to get information "
                                     "isn't active")
                        else:
                            pre = client.gencode.genpreference
                            members = get_client_list(client, charter=True,
                                                      gender_preference=pre)
                else:
                    log.debug("Trying to get a clients list for a"
                              "girls and not is a manager %s.", user.pk)
                    error = "You can't get information"
            else:
                log.debug("Trying to get a clients list with inactive user "
                          "code %s.", user.pk)
                error = "You aren't active"
        else:
            log.debug("Trying to get a clients list for a user doesn't"
                      "exits %s.", user.pk)
            error = 'You are not a user'
    else:
        min_age = request.POST.get('min_age')
        max_age = request.POST.get('max_age')
        country = request.POST.get('country')
        list_id = request.POST.get('list_id')
        members = get_client_list(user, min_age, max_age, country, list_id)

    if error:
        JsonResponse({'error': 'yes', 'description': error}, safe=False)
    else:
        if not members:
            return JsonResponse({'error': 'No results to show'}, safe=False)
        else:
            json_members = ExtJsonSerializer().serialize(
                members,
                default=convert_data_to_serielize,
                fields=['cliusername', 'cliname', 'age',
                        'clidescription', 'clibirthdate', 'citcode',
                        'marcode', 'educode', 'feecode', 'heicode',
                        'weicode', 'ocucode', 'ethcode', 'profile_picture',
                        'client_gallery'],
                indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True)
            return JsonResponse(json_members, safe=False)


def get_client_list(user, min_age=0, max_age=99,
                    country=None, list_id='',
                    gender_preference=1, charter=False):
    elexclude = ""
    elfiltro = Q(cliactive=True) & Q(
        clireplychannel__isnull=False) & Q(
        clidatesubscription__lte=datetime.now())
    if list_id:
        to_exclude = [int(n) for n in list_id.split(",")]
        elexclude = Q(clicode__in=to_exclude)

    if charter:
        elfiltro = elfiltro & Q(tclcode=4)
    else:
        # Si no estoy autenticado es que soy un cliente potencial
        if not user.is_authenticated:
            gender_preference = Gender.objects.filter(
                genpreference=gender_preference)
            # Como soy cliente potencial deben salir los charters y clients
            elfiltro = elfiltro & Q(tclcode__in=[4, 5])
        else:
            # Ya estoy autenticado, entonces soy charter, client o manager
            if user.last_name:
                json_gender = json.loads(user.last_name)
                gender_preference = Gender.objects.filter(
                    genpreference=json_gender['gen'])
                try:
                    # Si existe el cliente puedo saber que tipo de usuario es
                    c = Client.objects.get(clicode=user.id)
                    if (int(c.tclcode.tclcode) == 5 | int(
                                                    c.tclcode.tclcode) == 3):
                        # Si el usuario es manager o chatter mostrar solo
                        # clientes
                        elfiltro = elfiltro & Q(tclcode=4)
                    elif c.tclcode.tclcode == 4:
                        # Si el usuario es cliente, muestrame clientes y
                        # chartters
                        elfiltro = elfiltro & Q(tclcode__in=[4, 5])
                except Client.DoesNotExist:
                    # Si no existe el cliente, es un cliente potencial
                    elfiltro = elfiltro & Q(tclcode__in=[4, 5])

    elfiltro = elfiltro & Q(gencode=gender_preference)

    if min_age:
        from_min_date = date.today() - relativedelta(years=int(min_age))
        elfiltro = elfiltro & (Q(clibirthdate__lte=from_min_date) |
                               Q(clibirthdate=None))

    if max_age:
        from_max_date = date.today() - relativedelta(years=int(max_age) + 1)
        elfiltro = elfiltro & (Q(clibirthdate__gte=from_max_date) |
                               Q(clibirthdate=None))

    if country:
        country = City.objects.filter(coucode=country)
        elfiltro = elfiltro & Q(citcode__in=country)

    if elexclude:
        all_members = Client.objects.filter(elfiltro).exclude(elexclude)
    else:
        all_members = Client.objects.filter(elfiltro)

    if not all_members:
        all_members = Client.objects.filter(elfiltro)

    new_members = randomize(all_members, elexclude, elfiltro)

    return new_members


def randomize(all_members, elexclude, elfiltro):
    members = []
    for miembro in all_members:
        members.append(miembro.clicode)
    new_members = []
    if members:
        if len(members) > 18:
            while len(new_members) < 18:
                ran = random.choice(members)
                if len(new_members) > 0:
                    found = False
                    for m in new_members:
                        if ran == m.clicode:
                            found = True
                    if found is False:
                        new_members.append(Client.objects.get(clicode=ran))
                else:
                    new_members.append(Client.objects.get(clicode=ran))
        else:
            for m in members:
                new_members.append(Client.objects.get(clicode=m))

            if elexclude:
                all_members = Client.objects.filter(elfiltro)
                members = []
                for miembro in all_members:
                    members.append(miembro.clicode)

            while len(new_members) < 18:
                ran = random.choice(members)
                new_members.append(Client.objects.get(clicode=ran))

    return new_members


def get_client_albums(current_client, album=None):
    if not album:
        albums = PhotoAlbum.objects.filter(
            phaactive=True,
            clicode=current_client.pk).order_by(
            '-phacreationdate')
    else:
        albums = PhotoAlbum.objects.filter(phacode=album)

    album_list = []
    for album in albums:
        temp_album = {}
        temp_album['album'] = dict(
            id=album.phacode,
            name=album.phaname,
            description=album.phadescription,
            type=album.phatype,
            creationdate=album.phacreationdate)
        pictures = list(Picture.objects.filter(
            picactive=True, picprofile=False,
            phacode=album).values())
        if pictures:
            temp_album['pictures'] = pictures
            album_list.append(temp_album)

    return json.dumps(list(album_list), default=convert_data_to_serielize)


def ajax_room(request):
    # Look up the room from the channel session, bailing if it doesn't exist
    reciever = int(request.POST.get("reciever"))
    sender = request.user.pk

    if request.user.pk != int(request.POST.get("sender")):
        # Verificamos que entonces sea un manager
        sender = int(request.POST.get("sender"))
        cli_sen = Client.objects.get(clicode=request.user.pk)
        if cli_sen.tclcode.tclcode == 3:
            act_for_manager = ManagerClient.objects.filter(
                clicodemanager=request.user.pk,
                clicodegirl=sender).exists()
            if act_for_manager is False:
                log.debug("Manager with code %s is trying to get conversation "
                          "of girl %s", (message.user.pk, data['clicodesent']))
                return

    if sender < reciever:
        client1 = sender
        client2 = reciever
    else:
        client1 = reciever
        client2 = sender

    data = {}
    rooms = Room.objects.filter(
        clicode1=client1,
        clicode2=client2).order_by(
        "-roocode")
    if rooms:
        canti = 0
        i = 0
        newMessages = {}
        for room in rooms:
            # Marcamos que todos los mensajes fueron leidos
            upt = room.messages_room.filter(
                clicoderecieved=sender,
                mesread=False).update(
                mesread=True)
            messages = room.messages_room.order_by('-mescode')[:50]
            canti = canti + len(messages)
            for msg in messages:
                newMessages[i] = msg.as_dict()
                i = i + 1
            if canti >= 50:
                break

        resultMessage = {}
        for i in range(len(newMessages)):
            j = len(newMessages) - (i + 1)
            resultMessage[i] = newMessages[j]

        data["mensajes"] = resultMessage

    clientFilter = Client.objects.get(clicode=reciever).as_dict()
    data["cliente"] = clientFilter

    return HttpResponse(json.dumps(data), content_type='application/json')


def leave_conversation(request):
    if request.user.pk == int(request.POST.get("sender")):
        # Look up the room from the channel session,bailing if it doesn't exist
        if request.user.pk < int(request.POST.get("reciever")):
            client1 = request.user.pk
            client2 = request.POST.get("reciever")
        else:
            client1 = request.POST.get("reciever")
            client2 = request.user.pk

        data = {}
        rooms = Room.objects.filter(
            clicode1=client1,
            clicode2=client2).order_by(
            'roocode').last()
        if rooms:
            if rooms.roostartdatetime:
                if client1 == request.user.pk:
                    endclient = rooms.rooendclient1
                    enddatetime = rooms.rooendc1datetime
                    rooms.rooendclient1 = True
                else:
                    endclient = rooms.rooendclient2
                    enddatetime = rooms.rooendc2datetime
                    rooms.rooendclient2 = True
                if endclient is False:
                    cli_sen = Client.objects.get(
                        clicode=request.POST.get("sender"))
                    cli_rec = Client.objects.get(
                        clicode=request.POST.get("reciever"))
                    if cli_sen.fracode is None:
                        subservice = SubService.objects.get(suscode=1)
                        seg = timezone.now() - enddatetime

                        if seg.total_seconds() > 300:
                            seg = enddatetime - rooms.roostartdatetime
                            minute = int(seg.total_seconds() // 60) + 5
                        else:
                            seg = enddatetime - rooms.roostartdatetime
                            minute = int(seg.total_seconds() // 60)

                    debit = subservice.susquantitycredit * minute
                    credits = Purchase.credits(cli_sen)
                    debit = Record.record_chat(
                        cli_sen, cli_rec, debit,
                        credits, subservice, rooms)
                    if debit > 0:
                        cobrado = Purchase.debitCredits(cli_sen, debit)
                    rooms.save()

            credits = Purchase.credits(cli_sen)
            data["credits"] = credits
            data["error"] = "ok"
        else:
            data["error"] = "Conversation not found"
    else:
        data["error"] = "Problems with your log"
    return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_notifications(request):
    user = request.user
    girl = request.POST.get('girl')
    error = ""
    notifications = []

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == 3:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to get "
                              "notification with girl %s",
                              (user.pk, girl))
                    error = ("You don't have permission to get this kind "
                             "of information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = 'Not results to show'

    if error == "":
        i = 0
        exists = Notification.objects.filter(
            clicoderecieved=int(girl),
            notread=False).exists()
        if exists:
            noti = Notification.objects.filter(
                clicoderecieved=int(girl),
                notread=False)
            for n in noti:
                noti_detail = {}
                if n.ntycode.ntyactive:
                    noti_detail['notdescription'] = "@%s %s" % (
                        n.clicodesent.cliusername,
                        n.ntycode.ntydescription
                    )
                    noti_detail['notpicture'] = n.clicodesent.profile_picture
                    noti_detail['notdate'] = n.notdate
                    notifications.append(noti_detail)
                    i = i + 1
                    if i > 4:
                        break
        return JsonResponse(notifications, safe=False)
    else:
        return JsonResponse({'error': error}, safe=False)


def ajax_create_album(request):
    album_name = request.POST.get('album_name')
    album_type = request.POST.get('album_type')
    album_description = request.POST.get('album_description')
    pictures = request.POST.getlist('pictures[]')

    print(pictures)

    client = Client.objects.get(clicode=request.user.pk)

    album = PhotoAlbum()
    album_names = list(PhotoAlbum.objects.filter(
        clicode=client.clicode,
        phaactive=True).values_list(
        'phaname', flat=True))

    # Don't repeat album name
    if not album_name:
        album_name = datetime.now().date().isoformat()

    if album_name not in album_names:
        album.phaname = album_name
    else:
        count = 0
        while count <= len(album_names):
            new_name = "%s %s" % (album_name, count)
            if new_name not in album_names:
                album.phaname = new_name
                break
            count = count + 1
    album.phadescription = album_description
    album.phaactive = True
    album.phacreationdate = datetime.now().isoformat()
    album.phatype = album_type
    album.clicode = client
    album.save()

    picture = Picture()
    temp_files = UploadedFile.objects.filter(file_id__in=pictures)

    for pic in temp_files:
        picture = Picture(
            picpath=File(pic.uploaded_file, pic.original_filename),
            picactive=True,
            picprofile=False,
            phacode=album
        )
        picture.save()
        pic.uploaded_file.close()
        pic.delete()

    return JsonResponse({'message': 'success', 'album': album.phaname},
                        safe=False)
