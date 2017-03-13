from django.db import models
from .catalog import City


class Testimonial(models.Model):
    TESTIMONIAL_TYPE = (
        ('C', 'Comment'),
        ('L', 'Love Story'),
    )
    tescode = models.AutoField('Code', primary_key=True)
    tesname = models.CharField('Name', max_length=200)
    tesbirthdate = models.DateField(blank=True, null=True)
    tescomment = models.TextField('Comment')
    tespicture = models.ImageField('Picture', upload_to='testimonials')
    tesdate = models.DateField('Date')
    testype = models.CharField(
        'Testimonial Type', max_length=1, choices=TESTIMONIAL_TYPE)
    tesactive = models.BooleanField('Active')
    citcode = models.ForeignKey(City, models.DO_NOTHING,
                                db_column='citcode', blank=True, null=True,
                                related_name='testimonial_city')

    def __str__(self):
        return self.tesname

    class Meta:
        managed = True
        db_table = 'testimonial'
