from django.db import models


class Franchise(models.Model):
    fracode = models.AutoField(primary_key=True)
    fradescription = models.CharField(max_length=200)
    fraactive = models.BooleanField()

    def __str__(self):
        return self.fradescription

    class Meta:
        managed = True
        db_table = 'franchise'
