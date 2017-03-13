from django.db import models
import datetime
from django.utils import timezone
from django.utils.timezone import utc
from .catalog import Language
from .client import Client


class NotificationType(models.Model):
    ntycode = models.AutoField(primary_key=True)
    ntyname = models.CharField(max_length=40)
    ntydescription = models.CharField(max_length=250)
    ntyactive = models.BooleanField()

    def __str__(self):
        return self.ntydescription

    class Meta:
        managed = True
        db_table = 'notificationtype'


class NotificationTypeLanguage(models.Model):
    ntlcode = models.AutoField(primary_key=True)
    ntldescription = models.CharField(max_length=250)
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='notificationtylang_language')
    ntycode = models.ForeignKey(
                        NotificationType, models.DO_NOTHING,
                        db_column='ntycode',
                        related_name='notificationtylang_notificationty')

    def __str__(self):
        return self.ntldescription

    class Meta:
        managed = True
        db_table = 'notificationtype_language'


class Notification(models.Model):
    notcode = models.BigAutoField(primary_key=True)
    notdate = models.DateTimeField()
    notread = models.BooleanField(default=False)
    clicodesent = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodesent',
                                    related_name='notification_clientsent')
    clicoderecieved = models.ForeignKey(
                        Client, models.DO_NOTHING,
                        db_column='clicoderecieved',
                        related_name='notification_clientrecieved')
    ntycode = models.ForeignKey(NotificationType, models.DO_NOTHING,
                                db_column='ntycode',
                                related_name='notification_notificationtype')

    @property
    def ntymessage(self):
        msg = self.clicodesent.cliusername + " " + self.ntycode.ntydescription
        return msg

    @property
    def formatted_notdate(self):
        return self.notdate.strftime('%b %d,%Y %I:%M %p')

    def quantityNotRead(clicode):
        total = Notification.objects.filter(
            clicoderecieved=clicode, notread=False).count()
        return total

    def as_dict(self):
        return {
            'clientrecieved': self.clicoderecieved.clicode,
            'clientpicture': self.clicodesent.profile_picture,
            'ntymessage': self.ntymessage,
            'ntydate': self.notdate,
            'clientusername': self.clicodesent.cliusername,
        }

    class Meta:
        managed = True
        db_table = 'notification'
