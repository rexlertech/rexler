from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from .client import Client
from .catalog import Gender


class Network(models.Model):
    netcode = models.BigAutoField(primary_key=True)
    netdate = models.DateTimeField()
    clicodesent = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodesent',
                                    related_name='network_clientsent')
    clicoderecieved = models.ForeignKey(Client, models.DO_NOTHING,
                                        db_column='clicoderecieved',
                                        related_name='networks_clientrecieved')

    def __str__(self):
        return '%d %d' % (self.clicodesent, self.clicoderecieved)

    class Meta:
        managed = True
        db_table = 'network'


class BlockedClient(models.Model):
    blocode = models.AutoField(primary_key=True)
    blodate = models.DateTimeField()
    clicodesent = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodesent',
                                    related_name='client_blocked_to')
    clicoderecieved = models.ForeignKey(Client, models.DO_NOTHING,
                                        db_column='clicoderecieved',
                                        related_name='client_blocked_me')

    def __str__(self):
        return '%d %d' % (self.clicodesent, self.clicoderecieved)

    class Meta:
        managed = True
        db_table = 'blockedclient'


class ProfileVisit(models.Model):
    procode = models.BigAutoField(primary_key=True)
    prodate = models.DateTimeField()
    clicodesent = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodesent',
                                    related_name='profilevisit_clientsent')
    clicoderecieved = models.ForeignKey(
                        Client, models.DO_NOTHING,
                        db_column='clicoderecieved',
                        related_name='profilevisit_clientrecieved')

    def __str__(self):
        return '%d %d' % (self.clicodesent, self.clicoderecieved)

    class Meta:
        managed = True
        db_table = 'profilevisit'


class Search(models.Model):
    seacode = models.BigAutoField(primary_key=True)
    gencode = models.ForeignKey(Gender, models.DO_NOTHING, db_column='gencode',
                                blank=True, null=True, default=1,
                                related_name='search_gender')
    seaminage = models.SmallIntegerField("From", null=True, blank=True,
                                         default=18, validators=[
                                             MaxValueValidator(100),
                                             MinValueValidator(18)])
    seamaxage = models.SmallIntegerField("To", null=True, blank=True,
                                         default=30, validators=[
                                             MaxValueValidator(100),
                                             MinValueValidator(18)])
    seacountry = models.CharField(
        "Country", max_length=60, null=True, blank=True)
    seaonline = models.BooleanField("Online", default=False)
    seavideo = models.BooleanField("With video", default=False)
    seaphoto = models.BooleanField("Only photo", default=False)
    seaincome = models.CharField("Income", null=True)
    seamstatus = models.CharField("Marital Status", null=True)
    seaethnicity = models.CharField("Ethnicity", null=True)
    seafirstlang = models.CharField("First Language", null=True)
    seasecondlang = models.CharField("Second Language", null=True)
    seaocupation = models.CharField("Ocupation", null=True)
    seaheight = models.CharField("Height", null=True)
    seaweight = models.CharField("Weight", null=True)
    seachildren = models.SmallIntegerField("Children", null=True)
    seapet = models.CharField("Pet", null=True)
    seasport = models.CharField("Pet", null=True)
    seahobbie = models.CharField("Pet", null=True)

    def __str__(self):
        return '%d %d' % (self.seaminage, self.seamaxage)

    class Meta:
        managed = False


class Register(models.Model):
    regcode = models.BigAutoField(primary_key=True)
    regsignin = models.DateTimeField('Datetime to connect')
    regsignout = models.DateTimeField('Datetime to disconnect', blank=True,
                                      null=True)
    clicode = models.ForeignKey(Client, models.DO_NOTHING,
                                db_column='clicode',
                                related_name='log_client')

    def __str__(self):
        return self.logsignin

    class Meta:
        managed = True
        db_table = 'register'
