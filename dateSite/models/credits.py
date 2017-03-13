import json
import os.path
from django.db import models
from .client import Client, PhotoAlbum, ClientCollectionAlbum
from .purchase import Purchase, Record
from .service import SubService

def purch_album(request, album_added):
    client = Client.objects.get(clicode=request.user.pk)

    # Get current credits from user
    current_credits = Purchase.credits(client)
    credit_cost = SubService.objects.get(
        suscode=4)  # Number for view private album

    if current_credits < credit_cost.susquantitycredit:
        error_message = {}
        error_message["error"] = {'type': '4',
                                  'message': "Insufficient credits."}
        return json.dumps(error_message)
    else:
        album = PhotoAlbum.objects.get(phacode=album_added)
        member_album = Client.objects.get(clicode=album.clicode_id)

        record = Record(recdate=datetime.now().isoformat(),
                        suscode=credit_cost,
                        recdebit=credit_cost.susquantitycredit,
                        clicodemain=client,
                        clicodesecondary=member_album)
        record.save()

        debit = credit_cost.susquantitycredit
        purchase = Purchase.debitCredits(client, debit)

        collection = ClientCollectionAlbum.objects.filter(
            clicode=client,
            phacode=album)

        if not collection.exists():
            collection = ClientCollectionAlbum()
            collection.clicode = client
            collection.phacode = album
            collection.save()

        clisender = client.as_dict()
        clireciever = member_album.as_dict()
        clisender["credits"] = Purchase.credits(client)
        clireciever["credits"] = Purchase.credits(member_album)

        data = {}
        data["clisender"] = clisender
        data["clireciever"] = clireciever
        return json.dumps(data)
