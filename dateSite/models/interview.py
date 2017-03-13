from django.db import models
from .catalog import Language
from clients.models.client import Client


class Interview(models.Model):
    intcode = models.AutoField(primary_key=True)
    intdescription = models.CharField(max_length=100)
    intdate = models.DateTimeField()
    intobservation = models.TextField(blank=True, null=True)
    intactive = models.BooleanField()

    def __str__(self):
        return self.intdescription

    class Meta:
        managed = True
        db_table = 'interview'


class Question(models.Model):
    quecode = models.AutoField(primary_key=True)
    quedescription = models.CharField(max_length=200)
    queactive = models.BooleanField()
    intcode = models.ForeignKey(Interview, models.DO_NOTHING,
                                db_column='intcode',
                                related_name='question_interview')

    def __str__(self):
        return self.quedescription

    class Meta:
        managed = True
        db_table = 'question'


class QuestionClient(models.Model):
    qeccode = models.BigAutoField(primary_key=True)
    qecdate = models.DateTimeField()
    qecanswer = models.TextField(blank=True, null=True)
    quecode = models.ForeignKey(Question, models.DO_NOTHING,
                                db_column='quecode',
                                related_name='questionclient_question')
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode',
                                related_name='questionclient_client')

    def __str__(self):
        return self.qecanswer

    class Meta:
        managed = True
        db_table = 'question_client'


class QuestionLanguage(models.Model):
    qulcode = models.AutoField(primary_key=True)
    quldescription = models.CharField(max_length=200)
    quecode = models.ForeignKey(Question, models.DO_NOTHING,
                                db_column='quecode',
                                related_name='questionlanguage_question')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='questionlanguage_language')

    def __str__(self):
        return self.quldescription

    class Meta:
        managed = True
        db_table = 'question_language'
