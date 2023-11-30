# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Product(models.Model):
    productkey = models.SmallIntegerField(db_column='ProductKey', primary_key=True)  # Field name made lowercase.
    productcode = models.TextField(db_column='ProductCode')  # Field name made lowercase.
    productname = models.TextField(db_column='ProductName')  # Field name made lowercase.
    productdescription = models.TextField(db_column='ProductDescription', blank=True, null=True)  # Field name made lowercase.
    retailerkey = models.SmallIntegerField(db_column='RetailerKey')  # Field name made lowercase.
    programkey = models.SmallIntegerField(db_column='ProgramKey', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.productcode + ' (' + self.productdescription + ')'

    class Meta:
        managed = False
        db_table = 'product'
