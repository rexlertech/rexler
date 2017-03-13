import json
import os.path
from django.db import models
from datetime import datetime
from django.utils.text import Truncator
from django.utils.text import slugify
from django.contrib.auth.models import User
from .catalog import *
from .franchise import Franchise
from django.contrib.sites.models import Site


class Client(models.Model):
    cliuser = models.OneToOneField(User, on_delete=models.CASCADE)
    clicode = models.BigAutoField(primary_key=True)
    cliusername = models.CharField('username', max_length=30, blank=True,
                                   null=False)
    cliname = models.CharField('Name', max_length=30, blank=True, null=True)
    clifullname = models.CharField('Full Name', max_length=80,
                                   blank=True, null=True)
    clidescription = models.TextField('About', blank=True, null=True)
    clibirthdate = models.DateField('Birthdate', blank=True, null=True)
    clidatesubscription = models.DateTimeField()
    cliemail = models.CharField('Email', max_length=254, unique=True)
    clipassword = models.CharField('Password', max_length=128)
    clibalance = models.IntegerField('Balance', null=True, blank=True)
    cliactive = models.BooleanField('Active', null=False)
    clireplychannel = models.CharField('Websocket', max_length=30, null=True)
    cliverified = models.BooleanField('Verified', null=False, default = False)
    inccode = models.ForeignKey(Income, models.DO_NOTHING,
                                db_column='inccode', blank=True, null=True,
                                related_name='client_income')
    gencode = models.ForeignKey(Gender, models.DO_NOTHING,
                                db_column='gencode', blank=True, null=True,
                                related_name='client_gender')
    citcode = models.ForeignKey(City, models.DO_NOTHING,
                                db_column='citcode', blank=True, null=True,
                                related_name='client_city')
    marcode = models.ForeignKey(Marital, models.DO_NOTHING,
                                db_column='marcode', blank=True, null=True,
                                related_name='client_marital')
    educode = models.ForeignKey(Education, models.DO_NOTHING,
                                db_column='educode', blank=True, null=True,
                                related_name='client_education')
    bodycode = models.ForeignKey(BodyType, models.DO_NOTHING,
                                 db_column='bodcode', blank=True,
                                 null=True, related_name='client_bodytype')
    breastcode = models.ForeignKey(Breast, models.DO_NOTHING,
                                   db_column='brecode', blank=True,
                                   null=True, related_name='client_waist')
    waistcode = models.ForeignKey(Waist, models.DO_NOTHING,
                                  db_column='waicode', blank=True,
                                  null=True, related_name='client_butt')
    buttcode = models.ForeignKey(Butt, models.DO_NOTHING,
                                 db_column='butcode', blank=True,
                                 null=True, related_name='client_breast')
    eyecode = models.ForeignKey(EyesColor, models.DO_NOTHING,
                                db_column='eyecode', blank=True,
                                null=True, related_name='client_eyes')
    haicode = models.ForeignKey(HairColor, models.DO_NOTHING,
                                db_column='haicode', blank=True,
                                null=True, related_name='client_hair')
    hlecode = models.ForeignKey(HairLength, models.DO_NOTHING,
                                db_column='hlecode', blank=True,
                                null=True, related_name='client_hairlength')
    frecodedrink = models.ForeignKey(Frequency, models.DO_NOTHING,
                                     db_column='frecodedrink',
                                     blank=True, null=True,
                                     related_name='client_frequencydrink')
    frecodesmoke = models.ForeignKey(Frequency, models.DO_NOTHING,
                                     db_column='frecodesmoke',
                                     blank=True, null=True,
                                     related_name='client_frequencysmoke')
    lancodefirst = models.ForeignKey(Language, models.DO_NOTHING,
                                     db_column='lancodefirst', blank=True,
                                     null=True,
                                     related_name='client_first_language')
    lancodesecond = models.ForeignKey(Language, models.DO_NOTHING,
                                      db_column='lancodesecond', blank=True,
                                      null=True,
                                      related_name='client_second_language')
    langlevel = models.IntegerField('Languaje Level', null=True,
                                    blank=True)
    feecode = models.ForeignKey(Feeling, models.DO_NOTHING,
                                db_column='feecode', blank=True, null=True,
                                related_name='client_feeling')
    heicode = models.ForeignKey(Height, models.DO_NOTHING,
                                db_column='heicode', blank=True, null=True,
                                related_name='client_height')
    weicode = models.ForeignKey(Weight, models.DO_NOTHING,
                                db_column='weicode', blank=True, null=True,
                                related_name='client_weight')
    ocucode = models.ForeignKey(Occupation, models.DO_NOTHING,
                                db_column='ocucode', blank=True, null=True,
                                related_name='client_occupation')
    ethcode = models.ForeignKey(Ethnicity, models.DO_NOTHING,
                                db_column='ethcode', blank=True, null=True,
                                related_name='client_ethnicity')
    tclcode = models.ForeignKey(TypeClient, models.DO_NOTHING,
                                db_column='tclcode',
                                related_name='client_typeclient')
    fracode = models.ForeignKey(Franchise, models.DO_NOTHING,
                                db_column='fracode', blank=True, null=True,
                                related_name='franchise_code')
    relcode = models.ForeignKey(Religion, models.DO_NOTHING,
                                db_column='relcode', blank=True, null=True,
                                related_name='religion_code')
    zodcode = models.ForeignKey(Zodiac, models.DO_NOTHING,
                                db_column='zodcode', blank=True, null=True,
                                related_name='zodiac_code')
    chicode = models.ForeignKey(Children, models.DO_NOTHING,
                                db_column='chicode', blank=True, null=True,
                                related_name='children_code')

    def __str__(self):
        return self.cliusername

    @property
    def age(self):
        if self.clibirthdate:
            return int(
                (datetime.now().date() - self.clibirthdate).days / 365.25)
        return 0

    @property
    def hobbies(self):
        hobbies = []
        hob = HobbieClient.objects.filter(clicode=self.clicode)
        if hob:
            for h in hob:
                if h.hobcode.hobactive:
                    hobbies.append(h.hobcode.hobname)
        return hobbies

    @property
    def sports(self):
        sports = []
        spo = SportClient.objects.filter(clicode=self.clicode)
        if spo:
            for s in spo:
                if s.spocode.spoactive:
                    sports.append(s.spocode.sponame)
        return sports

    @property
    def pets(self):
        pets = []
        pet = PetClient.objects.filter(clicode=self.clicode)
        if pet:
            for p in pet:
                pet_detail = {}
                if p.petcode.petactive:
                    pet_detail["petname"] = p.petcode.petname
                    if p.pechave:
                        pet_detail["pechave"] = "Yes"
                    else:
                        pet_detail["pechave"] = "No"
                    if p.peclike:
                        pet_detail["peclike"] = "Yes"
                    else:
                        pet_detail["peclike"] = "No"
                    if p.pecdontlike:
                        pet_detail["pecdontlike"] = "Yes"
                    else:
                        pet_detail["pecdontlike"] = "No"
                    pets.append(pet_detail)

        return list(pets)

    @property
    def profile_picture(self):
        try:
            # 1 = Public album
            album = PhotoAlbum.objects.filter(
                clicode=self, phatype=1, phaactive=True)
            return str(Picture.objects.get(phacode__in=album, picprofile=True))
        except Picture.DoesNotExist:
            return '/media/clients_pictures/default.png'

    @property
    def feeling_picture(self):
        if self.feecode:
            return str(self.feecode.feeiconfile.url)
        return '/media/feelings/default.png'

    @property
    def client_gallery(self):
        album = PhotoAlbum.objects.filter(
            clicode=self, phatype=1, phaactive=True)
        pictures = Picture.objects.filter(
            phacode__in=album, picactive=True,
            picprofile=False)
        for picture in pictures:
            site = Site.objects.get_current()
            img = './media/%s' % str(picture.picpath)
            if not os.path.exists(img):
                picture.picactive = False
                picture.save()

        pictures = pictures.filter(picactive=True).order_by('-piccode')
        return list(pictures)

    @property
    def education(self):
        education = ""
        if self.educode:
            if self.educode.eduactive:
                education = self.educode.edudescription
        return education

    @property
    def ethnicity(self):
        ethnicity = ""
        if self.ethcode:
            if self.ethcode.ethactive:
                ethnicity = self.ethcode.ethname
        return ethnicity

    @property
    def marital(self):
        marital = ""
        if self.marcode:
            if self.marcode.maractive:
                marital = self.marcode.marname
        return marital

    @property
    def ocuppation(self):
        ocuppation = ""
        if self.ocucode:
            if self.ocucode.ocuactive:
                ocuppation = self.ocucode.ocudescription
        return ocuppation

    @property
    def firstlan(self):
        firstlan = ""
        if self.lancodefirst:
            firstlan = self.lancodefirst.lanname
        return firstlan

    @property
    def secondlan(self):
        secondlan = ""
        if self.lancodesecond:
            secondlan = self.lancodesecond.lanname
        return secondlan

    @property
    def income(self):
        income = ""
        if self.inccode:
            income = str(self.inccode.incmin) + " - " + \
                str(self.inccode.incmax)
        return income

    def total_members():
        total = Client.objects.count()
        return total

    def total_members_by_gender(gender):
        total = Client.objects.filter(gencode=gender).count()
        return total

    def total_members_online():
        total = Client.objects.exclude(clireplychannel__exact=None).count()
        return total

    def as_dict(self):
        return {
            'clicode': self.clicode,
            'cliname': self.cliname,
            'cliusername': self.cliusername,
            'clireplychannel': self.clireplychannel,
            'clipicture': self.profile_picture,
            'cliage': self.age,
            'gencode': self.gencode.gencode,
            'clicity': str(self.citcode),
            'clifeelingpicture': self.feeling_picture,
        }

    def client_complete(self):
        return {
            'clicode': self.clicode,
            'cliname': self.cliname,
            'cliusername': self.cliusername,
            'clidescription': self.clidescription,
            'clipicture': self.profile_picture,
            'cliage': self.age,
            'cligender': str(self.gencode.gendescription),
            'clicity': str(self.citcode),
            'clifeelingpicture': self.feeling_picture,
            'cliheight': str(self.heicode.heidescription),
            'cliweight': str(self.weicode.weidescription),
            'clieducation': str(self.education),
            'cliethnicity': str(self.ethnicity),
            'cliincome': str(self.income),
            'clilanfirst': str(self.firstlan),
            'clilansecond': str(self.secondlan),
            'climarital': str(self.marital),
            'cliocupation': str(self.ocuppation),
            'clihobbies': self.hobbies,
            'clisports': self.sports,
            'clipets': self.pets,
            'eyecode': self.eyecode,
            'haicode': self.haicode,
            'hlecode': self.hlecode,
            'clibirthdate': self.clibirthdate,
            'frecodedrink': self.frecodedrink,
            'frecodesmoke': self.frecodesmoke,
            'zodcode': self.zodcode,
            'chicode': self.chicode,
            'relcode': self.relcode,
            'bodycode': self.bodycode,
        }

    class Meta:
        managed = True
        db_table = 'client'


class ManagerClient(models.Model):
    maccode = models.BigAutoField(primary_key=True)
    clicodemanager = models.ForeignKey(
        Client, models.DO_NOTHING,
        db_column='clicodemanager',
        related_name='managerclient_manager')
    clicodegirl = models.ForeignKey(
        Client,
        models.DO_NOTHING,
        db_column='clicodegirl',
        related_name='managerclient_girl')

    class Meta:
        managed = True
        db_table = 'manager_client'


class PhotoAlbum(models.Model):
    ALBUM_TYPE = (
        ('1', 'Public'),
        ('2', 'Private'),
    )
    phacode = models.BigAutoField(primary_key=True)
    phaname = models.CharField('Name', max_length=50, blank=True, null=True)
    phadescription = models.CharField('Description', max_length=500,
                                      blank=True, null=True)
    phaactive = models.BooleanField('Active', null=False)
    phacreationdate = models.DateTimeField()
    phatype = models.CharField(max_length=1, choices=ALBUM_TYPE, default=1)
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode',
                                related_name='picture_client')

    def __str__(self):
        return self.phaname

    class Meta:
        managed = True
        db_table = 'album_client'


def get_user_image_folder(instance, filename):
    file_name = slugify(Truncator(filename).chars(20))
    if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        file_name = '%s.jpg' % file_name
    return "./clients_pictures/%s_%s/%s" % (
        instance.from_client.clicode,
        instance.from_client.cliusername,
        file_name)


class Picture(models.Model):
    piccode = models.BigAutoField(primary_key=True)
    picpath = models.ImageField(upload_to=get_user_image_folder,
                                default='clients_pictures/default.png')
    picdescription = models.CharField('Description', max_length=300,
                                      blank=True, null=True)
    phacode = models.ForeignKey(PhotoAlbum, models.DO_NOTHING,
                                db_column='phacode',
                                related_name='picture_album')
    picactive = models.BooleanField(default=True)
    picprofile = models.BooleanField(default=True)

    @property
    def from_client(self):
        album = PhotoAlbum.objects.get(phacode=self.phacode_id)
        user = Client.objects.get(clicode=album.clicode_id)
        return user

    def __str__(self):
        return self.picpath.url

    class Meta:
        managed = True
        db_table = 'picture_client'


class ClientCollectionAlbum(models.Model):
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode')
    phacode = models.ForeignKey(PhotoAlbum, models.DO_NOTHING,
                                db_column='phacode')

    class Meta:
        managed = True
        db_table = 'client_collection'


class PetClient(models.Model):
    peccode = models.BigAutoField(primary_key=True)
    pechave = models.BooleanField()
    peclike = models.BooleanField()
    pecdontlike = models.BooleanField()
    petcode = models.ForeignKey(Pet, models.DO_NOTHING, db_column='petcode',
                                related_name='petclient_pet')
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode',
                                related_name='petclient_client')

    def __str__(self):
        return self.petcode.petname

    class Meta:
        managed = True
        db_table = 'pet_client'


class SportClient(models.Model):
    spccode = models.BigAutoField(primary_key=True)
    clicode = models.ForeignKey(Client, models.DO_NOTHING,
                                db_column='clicode',
                                related_name='sportclient_client')
    spocode = models.ForeignKey(Sport, models.DO_NOTHING,
                                db_column='spocode',
                                related_name='sportclient_sport')

    def __str__(self):
        return '%s %s' % (self.clicode.cliusername, self.spocode.sponame)

    class Meta:
        managed = True
        db_table = 'sport_client'


class HobbieClient(models.Model):
    hoccode = models.BigAutoField(primary_key=True)
    hobcode = models.ForeignKey(Hobbie, models.DO_NOTHING, db_column='hobcode',
                                related_name='hobbieclient_hobbie')
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode',
                                related_name='hobbieclient_client')

    def __str__(self):
        return '%s %s' % (self.clicode.cliusername, self.hobcode.hobname)

    class Meta:
        managed = True
        db_table = 'hobbie_client'
