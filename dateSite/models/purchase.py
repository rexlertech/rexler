from django.db import models
from django.utils import timezone
from .service import SubService
from .chat import Room
from .client import Client
from django.db.models import IntegerField, Sum


class PlayPlan(models.Model):
    paycode = models.BigAutoField(primary_key=True)
    payname = models.CharField(max_length=100)
    paycredits = models.SmallIntegerField()
    payprice = models.SmallIntegerField()
    payunitprice = models.FloatField('Unit price')

    def __str__(self):
        return self.payname

    class Meta:
        managed = True
        db_table = 'payplan'


class Purchase(models.Model):
    purcode = models.BigAutoField(primary_key=True)
    purcredit = models.SmallIntegerField()
    purdate = models.DateTimeField()
    purstatus = models.CharField(max_length=40)
    purobservation = models.CharField(max_length=40, blank=True, null=True)
    purbalance = models.SmallIntegerField()
    paycode = models.ForeignKey(PlayPlan, models.DO_NOTHING,
                                db_column='paycode',
                                related_name='purchase_payplan')
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode',
                                related_name='purchase_client')

    def __str__(self):
        return self.purstatus

    def credits(client):
        result = 100000
        if client.fracode is None:
            result = 0
            p = Purchase.objects.filter(clicode=client.clicode,
                                        purstatus='ACTIVO').aggregate(
                Sum('purbalance'))
            if p["purbalance__sum"]:
                result = p["purbalance__sum"]
        return result

    def debitCredits(obj_client, debit):
        purchase = Purchase.objects.filter(
            clicode=obj_client.clicode,
            purbalance__gt=0,
            purstatus='ACTIVO').order_by('purcode')
        if purchase:
            cobrado = True
            i = 0
            while debit > 0:
                if len(purchase) > i:
                    balance = purchase[i].purbalance
                    new_balance = balance - debit
                    if new_balance >= 0:
                        debit, cobrado = 0, True
                    else:
                        new_balance = 0
                        debit = debit - balance
                    Purchase.objects.filter(
                                purcode=purchase[i].purcode).update(
                                purbalance=new_balance)
                    i = i + 1
        else:
            cobrado = False
        return cobrado

    class Meta:
        managed = True
        db_table = 'purchase'


class Record(models.Model):
    reccode = models.BigAutoField('Code', primary_key=True)
    recdate = models.DateTimeField('Date/Time',
                                   default=timezone.now, db_index=True)
    reccredit = models.IntegerField('Credit', blank=True, null=True)
    recdebit = models.IntegerField('Debit', blank=True, null=True)
    roocode = models.ForeignKey(Room, models.DO_NOTHING,
                                db_column='roocode', blank=True, null=True,
                                related_name='record_room')
    suscode = models.ForeignKey(SubService, models.DO_NOTHING,
                                db_column='suscode', blank=True, null=True,
                                related_name='record_subservice')
    purcode = models.ForeignKey(Purchase, models.DO_NOTHING,
                                db_column='purcode', blank=True, null=True,
                                related_name='record_purchase')
    clicodemain = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodemain',
                                    related_name='record_clientmain')
    clicodesecondary = models.ForeignKey(Client, models.DO_NOTHING,
                                         db_column='clicodesecondary',
                                         related_name='record_clientsecondary',
                                         blank=True,
                                         null=True)

    def record_chat(obj_cli_m, obj_cli_s, debit, credits, subservice, room):
        if credits > 0:
            record = Record.objects.filter(clicodemain=obj_cli_m.clicode,
                                           roocode=room.roocode,
                                           suscode=subservice.suscode)
            if record:
                if debit > record[0].recdebit:
                    new_debit = debit - record[0].recdebit
                    if credits > new_debit:
                        new_debit = debit
                        debit = debit - record[0].recdebit
                    else:
                        new_debit = debit
                        debit = credits
                    Record.objects.filter(reccode=record[0].reccode).update(
                        recdebit=new_debit)
                else:
                    debit = record[0].recdebit
            else:
                if debit > credits:
                    debit = credits
                record = Record.objects.create(
                    recdebit=debit,
                    suscode=subservice,
                    clicodemain=obj_cli_m,
                    clicodesecondary=obj_cli_s,
                    roocode=room)
        else:
            debit = 0
        return debit

    def record_sticker(obj_cli_m, obj_cli_s, debit,
                       credits, subservice, room):
        if credits > 0:
            record = Record.objects.create(
                recdebit=debit,
                roocode=room,
                suscode=subservice,
                clicodemain=obj_cli_m,
                clicodesecondary=obj_cli_s)
        return debit
