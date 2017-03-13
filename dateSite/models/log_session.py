from django.db import models
from datetime import datetime
from .client import Client


class LogSession(models.Model):
    logcode = models.BigAutoField(primary_key=True)
    logsignin = models.DateTimeField('Datetime to connect')
    logsignout = models.DateTimeField('Datetime to disconnect', blank=True,
                                      null=True)
    clicode = models.ForeignKey(Client, models.DO_NOTHING,
                                db_column='clicode',
                                related_name='log_client')

    def __str__(self):
        return self.logsignin

    class Meta:
        managed = True
        db_table = 'logsession'
