from django.db import models


class Language(models.Model):
    lancode = models.AutoField(primary_key=True)
    lanname = models.CharField(max_length=60)

    def __str__(self):
        return self.lanname

    class Meta:
        managed = True
        db_table = 'language'


class Country(models.Model):
    coucode = models.AutoField('Code', primary_key=True)
    couname = models.CharField('Name', max_length=100)
    couactive = models.BooleanField('Active')

    def __str__(self):
        return self.couname

    def natural_key(self):
        return (self.couname)

    class Meta:
        managed = True
        db_table = 'country'


class CountryLanguage(models.Model):
    colcode = models.AutoField(primary_key=True)
    colname = models.CharField(max_length=100)
    coucode = models.ForeignKey(Country, models.DO_NOTHING,
                                db_column='coucode',
                                related_name='countrylang_country')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='countrylang_language')

    def __str__(self):
        return self.colname

    class Meta:
        managed = True
        db_table = 'country_language'


class City(models.Model):
    citcode = models.AutoField('Code', primary_key=True)
    citname = models.CharField('Name', max_length=40)
    citactive = models.BooleanField('Active')
    coucode = models.ForeignKey(Country, models.DO_NOTHING,
                                db_column='coucode',
                                related_name='city_country')

    def __str__(self):
        return '%s, %s' % (self.citname, self.coucode)

    def natural_key(self):
        return '%s, %s' % (self.citname, self.coucode.natural_key())

    class Meta:
        managed = True
        db_table = 'city'


class CityLanguage(models.Model):
    cilcode = models.BigAutoField(primary_key=True)
    cilname = models.CharField(max_length=40)
    citcode = models.ForeignKey(City, models.DO_NOTHING,
                                db_column='citcode',
                                related_name='citylang_city')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='citylang_language')

    def __str__(self):
        return self.cilname

    class Meta:
        managed = True
        db_table = 'city_language'


class Education(models.Model):
    educode = models.AutoField(primary_key=True)
    edudescription = models.CharField(max_length=100)
    eduactive = models.BooleanField()

    def __str__(self):
        return self.edudescription

    class Meta:
        managed = True
        db_table = 'education'


class EducationLanguage(models.Model):
    edlcode = models.AutoField(primary_key=True)
    edldescription = models.CharField(max_length=100)
    educode = models.ForeignKey(Education, models.DO_NOTHING,
                                db_column='educode',
                                related_name='educationlang_education')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='educationlang_language')

    def __str__(self):
        return self.edldescription

    class Meta:
        managed = True
        db_table = 'education_language'


class Feeling(models.Model):
    feecode = models.AutoField(primary_key=True)
    feedescription = models.CharField(max_length=80)
    feeiconfile = models.ImageField('Icon', upload_to='feelings')
    feeactive = models.BooleanField()

    def __str__(self):
        return self.feedescription

    def natural_key(self):
        return self.feeiconfile.url

    class Meta:
        managed = True
        db_table = 'feeling'


class FeelingLanguage(models.Model):
    felcode = models.AutoField(primary_key=True)
    feldescription = models.CharField(max_length=80)
    feecode = models.ForeignKey(Feeling, models.DO_NOTHING,
                                db_column='feecode',
                                related_name='feelinglang_feeling')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='feelinglang_language')

    def __str__(self):
        return self.feldescription

    class Meta:
        managed = True
        db_table = 'feeling_language'


class Ethnicity(models.Model):
    ethcode = models.AutoField(primary_key=True)
    ethname = models.CharField(max_length=200)
    ethactive = models.BooleanField()

    def __str__(self):
        return self.ethname

    class Meta:
        managed = True
        db_table = 'ethnicity'


class EthnicityLanguage(models.Model):
    etlcode = models.AutoField(primary_key=True)
    etlname = models.CharField(max_length=200)
    ethcode = models.ForeignKey(Ethnicity, models.DO_NOTHING,
                                db_column='ethcode',
                                related_name='ethnicitylang_ethnicity')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='ethnicitylang_language')

    def __str__(self):
        return self.etlname

    class Meta:
        managed = True
        db_table = 'ethnicity_language'


class Gender(models.Model):
    gencode = models.AutoField(primary_key=True)
    genname = models.CharField(max_length=100)
    genpreference = models.PositiveSmallIntegerField(default=1, null=False)
    gendescription = models.CharField(max_length=250, blank=True, null=True)
    genactive = models.BooleanField()

    def natural_key(self):
        return self.gendescription

    def __str__(self):
        return self.gendescription

    class Meta:
        managed = True
        db_table = 'gender'


class GenderLanguage(models.Model):
    gelcode = models.AutoField(primary_key=True)
    gelname = models.CharField(max_length=100)
    geldescription = models.CharField(max_length=250, blank=True, null=True)
    gencode = models.ForeignKey(Gender, models.DO_NOTHING,
                                db_column='getcode',
                                related_name='genderlang_gender')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='genderlang_language')

    def __str__(self):
        return self.gelname

    class Meta:
        managed = True
        db_table = 'gender_language'


class Height(models.Model):
    heicode = models.AutoField(primary_key=True)
    heidescription = models.CharField(max_length=100)

    def __str__(self):
        return self.heidescription

    class Meta:
        managed = True
        db_table = 'height'


class Weight(models.Model):
    weicode = models.AutoField(primary_key=True)
    weidescription = models.CharField(max_length=100)

    def __str__(self):
        return self.weidescription

    class Meta:
        managed = True
        db_table = 'weight'


class Income(models.Model):
    inccode = models.AutoField(primary_key=True)
    incmin = models.IntegerField()
    incmax = models.IntegerField()

    def __str__(self):
        return '%d - %d' % (self.incmin, self.incmax)

    class Meta:
        managed = True
        db_table = 'income'


class Marital(models.Model):
    marcode = models.AutoField(primary_key=True)
    marname = models.CharField(max_length=100)
    maractive = models.BooleanField()

    def __str__(self):
        return self.marname

    class Meta:
        managed = True
        db_table = 'marital'


class MaritalLanguage(models.Model):
    malcode = models.AutoField(primary_key=True)
    malname = models.CharField(max_length=100)
    marcode = models.ForeignKey(Marital, models.DO_NOTHING,
                                db_column='marcode',
                                related_name='maritallang_marital')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='maritallang_language')

    def __str__(self):
        return self.malname

    class Meta:
        managed = True
        db_table = 'marital_language'


class Occupation(models.Model):
    ocucode = models.AutoField(primary_key=True)
    ocudescription = models.CharField(max_length=100)
    ocuactive = models.BooleanField()

    def __str__(self):
        return self.ocudescription

    class Meta:
        managed = True
        db_table = 'occupation'


class OccupationLanguage(models.Model):
    oclcode = models.AutoField(primary_key=True)
    oclname = models.CharField(max_length=100)
    ocucode = models.ForeignKey(Occupation, models.DO_NOTHING,
                                db_column='ocucode',
                                related_name='occupationlang_occupation')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='occupationlang_language')

    def __str__(self):
        return self.oclname

    class Meta:
        managed = True
        db_table = 'occupation_language'


class TypeClient(models.Model):
    tclcode = models.AutoField(primary_key=True)
    tcldescription = models.CharField(max_length=30)
    tclactive = models.BooleanField()

    def __str__(self):
        return self.tcldescription

    class Meta:
        managed = True
        db_table = 'typeclient'


class Pet(models.Model):
    petcode = models.AutoField(primary_key=True)
    petname = models.CharField(max_length=200)
    petactive = models.BooleanField()

    def __str__(self):
        return self.petname

    class Meta:
        managed = True
        db_table = 'pet'


class PetLanguage(models.Model):
    pelcode = models.AutoField(primary_key=True)
    pelname = models.CharField(max_length=200)
    petcode = models.ForeignKey(Pet, models.DO_NOTHING, db_column='petcode',
                                related_name='petlang_pet')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='petlang_language')

    def __str__(self):
        return self.pelname

    class Meta:
        managed = True
        db_table = 'pet_language'


class Sport(models.Model):
    spocode = models.AutoField(primary_key=True)
    sponame = models.CharField(max_length=200)
    spoactive = models.BooleanField()

    def __str__(self):
        return self.sponame

    class Meta:
        managed = True
        db_table = 'sport'


class SportLanguage(models.Model):
    splcode = models.AutoField(primary_key=True)
    splname = models.CharField(max_length=200)
    spocode = models.ForeignKey(Sport, models.DO_NOTHING,
                                db_column='spocode',
                                related_name='sportlang_sport')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='sportlang_language')

    def __str__(self):
        return self.splname

    class Meta:
        managed = True
        db_table = 'sport_language'


class Hobbie(models.Model):
    hobcode = models.AutoField(primary_key=True)
    hobname = models.CharField(max_length=200)
    hobactive = models.BooleanField()

    def __str__(self):
        return self.hobname

    class Meta:
        managed = True
        db_table = 'hobbie'


class HobbieLanguage(models.Model):
    holcode = models.AutoField(primary_key=True)
    holname = models.CharField(max_length=200)
    hobcode = models.ForeignKey(Hobbie, models.DO_NOTHING,
                                db_column='hobcode',
                                related_name='hobbielang_hobbie')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='hobbielang_language')

    def __str__(self):
        return self.holname

    class Meta:
        managed = True
        db_table = 'hobbie_language'


class SkinTone(models.Model):
    skicode = models.AutoField('Code', primary_key=True)
    skiname = models.CharField('Tone', max_length=100)
    skiactive = models.BooleanField('Active')

    def __str__(self):
        return self.skiname

    def natural_key(self):
        return (self.skiname)

    class Meta:
        managed = True
        db_table = 'skintone'


class SkinToneLanguage(models.Model):
    sklcode = models.AutoField(primary_key=True)
    sklname = models.CharField(max_length=100)
    skicode = models.ForeignKey(SkinTone, models.DO_NOTHING,
                                db_column='skicode',
                                related_name='skinlang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='skinlang_language')

    def __str__(self):
        return self.sklname

    class Meta:
        managed = True
        db_table = 'skintone_language'


class Zodiac(models.Model):
    zodcode = models.AutoField('Code', primary_key=True)
    zodname = models.CharField('Name', max_length=100)
    zodactive = models.BooleanField('Active')

    def __str__(self):
        return self.zodname

    def natural_key(self):
        return (self.zodname)

    class Meta:
        managed = True
        db_table = 'zodiacsign'


class ZodiacLanguage(models.Model):
    zolcode = models.AutoField(primary_key=True)
    zolname = models.CharField(max_length=100)
    zodcode = models.ForeignKey(Zodiac, models.DO_NOTHING,
                                db_column='zodcode',
                                related_name='zodiaclang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='zodiaclang_language')

    def __str__(self):
        return self.zolname

    class Meta:
        managed = True
        db_table = 'zodiac_language'


class Religion(models.Model):
    relcode = models.AutoField('Code', primary_key=True)
    relname = models.CharField('Name', max_length=100)
    relactive = models.BooleanField('Active')

    def __str__(self):
        return self.relname

    def natural_key(self):
        return (self.relname)

    class Meta:
        managed = True
        db_table = 'religion'


class ReligionLanguage(models.Model):
    rlcode = models.AutoField(primary_key=True)
    rlname = models.CharField(max_length=100)
    relcode = models.ForeignKey(Religion, models.DO_NOTHING,
                                db_column='relcode',
                                related_name='religionlang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='religionlang_language')

    def __str__(self):
        return self.zolname

    class Meta:
        managed = True
        db_table = 'religion_language'


class BodyType(models.Model):
    bodcode = models.AutoField('Code', primary_key=True)
    bodname = models.CharField('Name', max_length=100)
    bodactive = models.BooleanField('Active')

    def __str__(self):
        return self.bodname

    def natural_key(self):
        return (self.bodname)

    class Meta:
        managed = True
        db_table = 'bodytype'


class BodyTypeLanguage(models.Model):
    bolcode = models.AutoField(primary_key=True)
    bolname = models.CharField(max_length=100)
    bodcode = models.ForeignKey(BodyType, models.DO_NOTHING,
                                db_column='bodcode',
                                related_name='bodytypelang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='bodytypelang_language')

    def __str__(self):
        return self.bolname

    class Meta:
        managed = True
        db_table = 'bodytype_language'


class Breast(models.Model):
    brecode = models.AutoField('Code', primary_key=True)
    brename = models.CharField('Name', max_length=100)
    breactive = models.BooleanField('Active')

    def __str__(self):
        return self.brename

    def natural_key(self):
        return (self.brename)

    class Meta:
        managed = True
        db_table = 'breast'


class Waist(models.Model):
    waicode = models.AutoField('Code', primary_key=True)
    wainame = models.CharField('Name', max_length=100)
    waiactive = models.BooleanField('Active')

    def __str__(self):
        return self.wainame

    def natural_key(self):
        return (self.wainame)

    class Meta:
        managed = True
        db_table = 'waist'


class Butt(models.Model):
    butcode = models.AutoField('Code', primary_key=True)
    butname = models.CharField('Name', max_length=100)
    butactive = models.BooleanField('Active')

    def __str__(self):
        return self.butname

    def natural_key(self):
        return (self.butname)

    class Meta:
        managed = True
        db_table = 'butt'


class EyesColor(models.Model):
    eyecode = models.AutoField('Code', primary_key=True)
    eyename = models.CharField('Name', max_length=100)
    eyeactive = models.BooleanField('Active')

    def __str__(self):
        return self.eyename

    def natural_key(self):
        return (self.eyename)

    class Meta:
        managed = True
        db_table = 'eyescolor'


class EyesColorLanguage(models.Model):
    eylcode = models.AutoField(primary_key=True)
    eylname = models.CharField(max_length=100)
    eyecode = models.ForeignKey(EyesColor, models.DO_NOTHING,
                                db_column='eyecode',
                                related_name='eyeslang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='eyescolorlang_language')

    def __str__(self):
        return self.eylname

    class Meta:
        managed = True
        db_table = 'eyescolor_language'


class HairColor(models.Model):
    haicode = models.AutoField('Code', primary_key=True)
    hainame = models.CharField('Name', max_length=100)
    haiactive = models.BooleanField('Active')

    def __str__(self):
        return self.hainame

    def natural_key(self):
        return (self.hainame)

    class Meta:
        managed = True
        db_table = 'haircolor'


class HairColorLanguage(models.Model):
    halcode = models.AutoField(primary_key=True)
    halname = models.CharField(max_length=100)
    haicode = models.ForeignKey(HairColor, models.DO_NOTHING,
                                db_column='haicode',
                                related_name='hairlang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='haircolorlang_language')

    def __str__(self):
        return self.halname

    class Meta:
        managed = True
        db_table = 'haircolor_language'


class HairLength(models.Model):
    hlecode = models.AutoField('Code', primary_key=True)
    hlename = models.CharField('Name', max_length=100)
    hleactive = models.BooleanField('Active')

    def __str__(self):
        return self.hlename

    def natural_key(self):
        return (self.hlename)

    class Meta:
        managed = True
        db_table = 'hairlength'


class HairLengthLanguage(models.Model):
    hllcode = models.AutoField(primary_key=True)
    hllname = models.CharField(max_length=100)
    hlecode = models.ForeignKey(HairLength, models.DO_NOTHING,
                                db_column='hlecode',
                                related_name='hairlengthlang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='hairlengthlang_language')

    def __str__(self):
        return self.hllname

    class Meta:
        managed = True
        db_table = 'hairlength_language'


class Children(models.Model):
    chicode = models.AutoField('Code', primary_key=True)
    chiname = models.CharField('Name', max_length=100)
    chiactive = models.BooleanField('Active')

    def __str__(self):
        return self.chiname

    def natural_key(self):
        return (self.chiname)

    class Meta:
        managed = True
        db_table = 'children'


class ChildrenLanguage(models.Model):
    chlcode = models.AutoField(primary_key=True)
    chlname = models.CharField(max_length=100)
    chicode = models.ForeignKey(Children, models.DO_NOTHING,
                                db_column='chicode',
                                related_name='childrenlang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='childrenlang_language')

    def __str__(self):
        return self.chlname

    class Meta:
        managed = True
        db_table = 'children_language'


class Frequency(models.Model):
    frecode = models.AutoField('Code', primary_key=True)
    frename = models.CharField('Name', max_length=100)
    freactive = models.BooleanField('Active')

    def __str__(self):
        return self.frename

    def natural_key(self):
        return (self.frename)

    class Meta:
        managed = True
        db_table = 'frequency'


class FrequencyLanguage(models.Model):
    fqlcode = models.AutoField(primary_key=True)
    fqlname = models.CharField(max_length=100)
    frecode = models.ForeignKey(Frequency, models.DO_NOTHING,
                                db_column='frecode',
                                related_name='frequencylang')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode',
                                related_name='frequencylang_language')

    def __str__(self):
        return self.fqlname

    class Meta:
        managed = True
        db_table = 'frequency_language'
