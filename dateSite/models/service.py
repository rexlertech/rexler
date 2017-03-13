from django.db import models
from .catalog import Language


class Service(models.Model):
    sercode = models.AutoField(primary_key=True)
    sername = models.CharField(max_length=100)
    seractive = models.BooleanField()

    def __str__(self):
        return self.sername

    class Meta:
        managed = True
        db_table = 'service'


class ServiceLanguage(models.Model):
    selcode = models.AutoField(primary_key=True)
    selname = models.CharField(max_length=100)
    sercode = models.ForeignKey(Service, models.DO_NOTHING,
                                db_column='sercode',
                                related_name='servicelang_service')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='servicelang_language')

    def __str__(self):
        return self.selname

    class Meta:
        managed = True
        db_table = 'service_language'


class SubService(models.Model):
    suscode = models.AutoField(primary_key=True)
    susdescription = models.CharField(max_length=60)
    susquantitycredit = models.SmallIntegerField()
    susactive = models.BooleanField()
    sercode = models.ForeignKey(Service, models.DO_NOTHING,
                                db_column='sercode',
                                related_name='subservice_service')

    def __str__(self):
        return self.susdescription

    class Meta:
        managed = True
        db_table = 'subservice'


class SubServiceLanguage(models.Model):
    sulcode = models.AutoField(primary_key=True)
    suldescription = models.CharField(max_length=60)
    suscode = models.ForeignKey(SubService, models.DO_NOTHING,
                                db_column='suscode',
                                related_name='subservicelang_subservice')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='subservicelang_language')

    def __str__(self):
        return self.suldescription

    class Meta:
        managed = True
        db_table = 'subservice_language'
