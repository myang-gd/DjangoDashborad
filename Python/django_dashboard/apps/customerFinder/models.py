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

class Project(models.Model):
    
    name = models.CharField(max_length=50, db_column='Name')
    projectId = models.IntegerField(primary_key=True, db_column='ProjectId')    
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return self.name
    
    class Meta:
        managed = False
        db_table = 'Project'


class ProductMap(models.Model):
    
    name = models.CharField(max_length=50, blank=True, null=False, db_column='Name')  # Field name made lowercase.
    productKey = models.CharField(max_length=500, blank=True, null=True, db_column='ProductKey')  # Field name made lowercase.
    ipsProductKey = models.CharField(max_length=500, blank=True, null=True, db_column='IPSProductKey')  # Field name made lowercase.
    projectKey = models.ForeignKey(Project, db_column='ProjectKey')    
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return self.name
    
    class Meta:
        managed = False
        db_table = 'ProductMap'



class CustomerType(models.Model):

    name = models.CharField(max_length=50, blank=True, null=False, db_column='Name')
    isConfigurable = models.CharField(max_length=50, blank=True, null=False, db_column='IsConfigurable')
    isVisible = models.BooleanField()        
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        managed = False
        db_table = 'CustomerType'

class Sqlquery(models.Model):
    
    querykey = models.IntegerField(primary_key=True, db_column='QueryKey')
    sqlcommand = models.CharField(max_length=20, blank=True, null=False, db_column='SQLCommand')  # Field name made lowercase.
    selectlistitem = models.CharField(max_length=200, blank=True, null=True, db_column='SelectListItem')
    tablelistitem = models.CharField(max_length=200, blank=True, null=True, db_column='TableListItem')
    alias = models.CharField(max_length=20, blank=True, null=False, db_column='Alias')  # Field name made lowercase.
    joinlistitem = models.CharField(max_length=200, blank=True, null=True, db_column='JoinListItem')  # Field name made lowercase.
    joincondition = models.CharField(max_length=2000, blank=True, null=True, db_column='JoinCondition')
    filtercondition = models.CharField(max_length=2000, blank=True, null=True, db_column='FilterCondition') # Field name made lowercase.
    filterparam = models.CharField(max_length=50, blank=True, null=True, db_column='FilterParam')  # Field name made lowercase.
    appendsqlquery = models.CharField(max_length=2000, blank=True, null=True, db_column='AppendSQLQuery')    
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return str(self.querykey)
    
    class Meta:
        managed = False
        db_table = 'SQLQuery'
        
class TableList(models.Model):
    customertypekey = models.IntegerField(primary_key=True, db_column='CustomerTypeKey')  # Field name made lowercase.
    name = models.CharField(max_length=50, blank=True, null=False, db_column='Name')
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        managed = False
        db_table = 'CustomerType'
    
class EmailPrefix(models.Model):

    customertypekey = models.IntegerField(primary_key=True, db_column='CustomerTypeKey')  # Field name made lowercase.
    name = models.CharField(max_length=50, blank=True, null=False, db_column='Name')
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        managed = False
        db_table = 'CustomerType'

    
class UserIDPrefix(models.Model):        
    
    customertypekey = models.IntegerField(primary_key=True, db_column='CustomerTypeKey')  # Field name made lowercase.
    name = models.CharField(max_length=50, blank=True, null=False, db_column='Name')
    createDate = models.DateTimeField(auto_now_add=True, db_column='CreateDate')  # Field name made lowercase.
    changeDate = models.DateTimeField(auto_now_add=True, db_column='ChangeDate')  # Field name made lowercase.
    changeBy = models.CharField(max_length=50, blank=True, null=True, db_column='changeBy')  # Field name made lowercase.
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        managed = False
        db_table = 'CustomerType'
    
                    