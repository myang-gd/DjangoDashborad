# from __future__ import unicode_literals

from django.db import models
from common_utils.str_util import StrUtil

FIELD_VALUE_MAX = 5000

class Environments(models.Model):
#     id = models.IntegerField()
    environment = models.CharField(max_length=10)
    enabled = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'environments'
        app_label = 'ConfigModifier'
    def __str__(self):  
        return self.environment

class ExclusiveMap(models.Model):
#     id = models.IntegerField()
    left_value = models.IntegerField()
    right_value = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'exclusive_map'

class Project(models.Model):
    name = models.CharField(max_length=50, blank=True)
    display_name = models.CharField(max_length=50,blank=True)
    class Meta:
        db_table = 'project'
    def __str__(self):  
        return ('%s' %(str(self.display_name))) 

class ServerTier(models.Model):
    name = models.CharField(max_length=50, blank=True, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        db_table = 'server_tier'
    def __str__(self):  
        return ('%s' %(str(self.name)))

class ServerTypes(models.Model):
    project = models.ForeignKey(Project, db_column='project', blank=True, null=True)
    server_tier = models.ForeignKey(ServerTier, db_column='server_tier', blank=True, null=True )
    is_cloud = models.BooleanField(default=False)
    def __str__(self): 
        #return  self.server_type
        return ('%s%s%s' %(StrUtil.str_none(self.project), ( '_' if StrUtil.str_none(self.project) != '' and StrUtil.str_none(self.server_tier) !='' else ''), StrUtil.str_none(self.server_tier)))
        #return ('%s%s' %(str(self.project.name).upper()+"_" if self.project else "", str(self.server_type).upper()))
    class Meta:
        managed = True
        db_table = 'server_types'
        ordering = ("project__name", "server_tier__name")
    @staticmethod
    def getByName(name):
        if '_' in name:
            project = name.split('_')[0].strip().upper()
            tier = name.split('_')[1].strip().upper()
            server_type = ServerTypes.objects.filter(project__name=project, server_tier__name=tier).first()
        else:
            server_type = ServerTypes.objects.filter(server_tier__name=name).first()
        return server_type
        
class FileTypes(models.Model):
    file_type = models.CharField(max_length=50)
    XML,JSON = ('XML','JSON')
    def __str__(self):  
        return self.file_type
    class Meta:
        managed = False
        db_table = 'file_types'

class Filemap(models.Model):
#     id = models.AutoField(primary_key=True)
    SERVER_TYPE, FILE_NAME, LOCATION = ('server_type','filename','location')
    server_type = models.ForeignKey(ServerTypes, db_column='server_type' )
    filename = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255)
    file_type = models.ForeignKey(FileTypes, db_column='file_type', blank=True, null=True)
    
    def __str__(self):  
        return str(self.id)+'_'+str(self.server_type)+ '_' + str(self.location) + '\\' + str(self.filename)
    class Meta:
        managed = False
        db_table = 'filemap'
        
class Priority(models.Model):
    LOW,NORMAL,HIGH = ('Low','Normal','High')
    NAME,DELAY=('name','delay')
    name = models.CharField(max_length=50)
    delay = models.IntegerField()
    class Meta:
        db_table = 'priority'
    def __str__(self):  
        return ('%s' %(str(self.name)))
    
  
class Fields(models.Model):
#     id = models.IntegerField()
    FILE_ID,ELEMENT_PATH,NEEDS_APPROVAL,ATTRIBUTE,PARENT_ID,TO_DISPLAY = ('file_id','element_path','needs_approval','attribute','parent_id','to_display')
    DISPLAY,NAMESPACE,REMOVE_FIELD,REMOVE_ATTRIBUTE,ENABLED,ADMIN_NOTIFIED_DATE = ('display','namespace','remove_field','remove_attribute','enabled','admin_notified_date')
    ADD_ENTRY,CHANGE_NEED_VALIDATE,PRIORITY= ('add_entry','change_need_validate','priority')
    file_id = models.ForeignKey(Filemap, db_column='file_id', blank=True, null=True) 
    element_path = models.CharField(max_length=250)
    needs_approval = models.BooleanField(default=False) # NullBooleanField change to BooleanField to prevent user input null value
    attribute = models.CharField(max_length=250, blank=True)
    parent_id = models.IntegerField(blank=True, null=True)
    to_display = models.BooleanField(default=False)# NullBooleanField change to BooleanField to prevent user input null value
    display = models.CharField(max_length=1500, blank=True, null=True)
    namespace = models.CharField(max_length=250, blank=True, null=True, default=None)
    remove_field = models.BooleanField()
    remove_attribute = models.BooleanField()
    enabled = models.BooleanField()
    admin_notified_date = models.DateTimeField(blank=True, null=True)
    priority = models.ForeignKey(Priority, db_column='priority', blank=True, null=True, default=1) 
    def __str__(self):  
        return str(self.id)+'_'+str(self.display)
    class Meta:
        managed = True
        db_table = 'fields'

class ValueTypes(models.Model):
    value_type = models.CharField(max_length=50)
    JSON_STR,JSON_NUM,STR = ('JSON_STR','JSON_NUM','STR')
    def __str__(self):  
        return self.value_type
    class Meta:
        managed = True
        db_table = 'value_types'

class LockStates(models.Model):
    status_type = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    CANC_DEP,P_AUTH,P_DEP,P_OTHER = ('CANC_DEP','P_AUTH','P_DEP', 'P_OTHER')
    def __str__(self):  
        return self.status_type
    class Meta:
        managed = True
        db_table = 'lock_states'
               
class FieldDefaultMap(models.Model):
#     id = models.IntegerField()
    default_value = models.TextField()
    environment_id = models.ForeignKey(Environments, db_column='environment_id', blank=True, null=True)
    field_id = models.ForeignKey(Fields, db_column='field_id', blank=True, null=True)
    time_stamp = models.DateTimeField(blank=True, null=True)
    server_id = models.IntegerField(blank=True, null=True)
    value_type = models.ForeignKey(ValueTypes, db_column='value_type', blank=True, null=True)
                                   
    class Meta:
        managed = False
        db_table = 'field_default_map'
     
    def __str__(self):  
        return str(self.field_id)+'_'+str(self.environment_id)+'_'+str(self.default_value)

class GdUser(models.Model):
#     id = models.IntegerField()
    login = models.CharField(max_length=50)
    empowered = models.NullBooleanField()
    cm = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'gd_user'    
    def __str__(self):  
        return str(self.login)

class Servers(models.Model):
#     id = models.IntegerField()
    ENVIRONMENT_ID, SERVER_NAME, SERVER_TYPE, ENABLED = ('environment_id','server_name','server_type','enabled')
    environment_id = models.ForeignKey(Environments, db_column='environment_id',blank=True, null=True)
    server_name = models.CharField(max_length=50)
    server_type = models.ForeignKey(ServerTypes, db_column='server_type', blank=True, null=True)
    enabled = models.BooleanField()
    re_notified_date = models.DateTimeField(blank=True, null=True)
    warnings = models.IntegerField()
    class Meta:
        managed = True
        db_table = 'servers'
    def __str__(self):  
        return ('%s_%s' %(str(self.server_name), str(self.server_type)))
              
class CurrentLocks(models.Model):
#     id = models.IntegerField()
    VALUE,DURATION,STARTDATE,REQUESTTIME,USER_ID,FIELD_ID,ENVIRONMENT_ID= ('value','duration','startdate','requesttime','user_id','field_id','environment_id')
    IS_ACTIVE,IS_COMPLETE,IS_CANCELLED,SERVER_ID = ('is_active','is_complete','is_cancelled','server_id')
    
    value = models.CharField(max_length=FIELD_VALUE_MAX, blank=True)
    duration = models.IntegerField()
    startdate = models.DateTimeField(db_column='startDate', blank=True, null=True)  # Field name made lowercase.
    requesttime = models.DateTimeField(db_column='requestTime', blank=True, null=True)  # Field name made lowercase.
    user_id = models.ForeignKey(GdUser, db_column='user_id')
    field_id =  models.ForeignKey(Fields, db_column='field_id')
    environment_id = models.ForeignKey(Environments, db_column='environment_id')
    is_active = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    server_id = models.ForeignKey(Servers, db_column='server_id')
    value_type = models.ForeignKey(ValueTypes, db_column='value_type', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'current_locks'
        
    def __str__(self):         
        return ('%s_%s_%s_%s_%s' %(str(self.field_id),str(self.user_id),str(self.environment_id),str(self.duration),str(self.value)))
    
class Types(models.Model):
#     id = models.IntegerField()
    datatype = models.CharField(max_length=10)
    has_values = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'types'
    def __str__(self):         
        return str(self.datatype)   
    
class ValidationTypes(models.Model):
#     id = models.IntegerField()
    type = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'validation_types'
        
    def __str__(self):  
        return ('%s' %(str(self.type)))
    
class FieldValidations(models.Model):
#     id = models.IntegerField()
    field_id = models.ForeignKey(Fields, db_column='field_id')
    type = models.ForeignKey(ValidationTypes, db_column='type')
    validation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'field_validations'
    def __str__(self):         
        return ('%s_%s_%s' %(str(self.field_id),str(self.type),str(self.validation)))

class FieldParams(models.Model):
    #id = models.IntegerField()
    field_id =  models.ForeignKey(Fields, db_column='field_id')
    param = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    value_type = models.ForeignKey(ValueTypes, db_column='value_type', blank=True, null=True)
    def __str__(self):  
        return ('%s_%s:%s' %(str(self.id), str(self.param), str(self.value)))
    class Meta:
        managed = False
        db_table = 'field_params'


class FieldValues(models.Model):
#     id = models.IntegerField()
    FIELD_VALUE = 'field_value'
    field_id =  models.ForeignKey(Fields, db_column='field_id')
    field_value = models.TextField()
    value_type = models.ForeignKey(ValueTypes, db_column='value_type', blank=True, null=True)
    
    def __str__(self):  
        return ('%s_value=%s' %(str(self.id), str(self.field_value)))
    class Meta:
        managed = False
        db_table = 'field_values'       


class FieldsStatus(models.Model):
#     id = models.IntegerField()
    enabled = models.BooleanField()
    environment_id =  models.ForeignKey(Environments, db_column='environment_id')
    field_id = models.ForeignKey(Fields, db_column='field_id')
    warnings = models.IntegerField()
    server_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fields_status'

    def __str__(self):  
        return ('%s_%s_%s_%s' %(str(self.field_id), str(self.environment_id), str(self.server_id), str(self.enabled)))


class FilemapStatus(models.Model):
#     id = models.IntegerField()
    filemap_id = models.ForeignKey(Filemap, db_column='filemap_id')
    environment_id = models.ForeignKey(Environments, db_column='environment_id')
    failure_reason = models.IntegerField()
    re_notified_date = models.DateTimeField(blank=True, null=True)
    warnings = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'filemap_status'
    def __str__(self):  
        return ('%s_%s_%s' %(str(self.filemap_id), str(self.environment_id), str(self.failure_reason)))

class LockAction(models.Model):
    action = models.CharField(max_length=50)
    ACTIVATE,RELEASE,RESET = ('ACTIVATE','RELEASE', 'RESET')
    def __str__(self):  
        return self.action
    class Meta:
        db_table = 'lock_action'
        
class FilemapTrace(models.Model):
    filemap_id = models.ForeignKey(Filemap, db_column='filemap_id')
    lock_id = models.ForeignKey(CurrentLocks, db_column='lock_id')
    lock_action = models.ForeignKey(LockAction, db_column='lock_action')
    lock_time = models.DateTimeField(db_column='lock_time', blank=True, null=True)
    system_time = models.DateTimeField(db_column='system_time', blank=True, null=True)
    class Meta:
        db_table = 'filemap_trace'
    def __str__(self):  
        return ('%s_%s' %(str(self.filemap_id), str(self.lock_id)))

class SessionTable(models.Model):
    user_id = models.IntegerField()
    sessionid = models.CharField(db_column='sessionId', max_length=250)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'session_table'


class SuspendActivity(models.Model):
    suspend = models.BooleanField()
    suspender = models.ForeignKey(GdUser, db_column='suspender')
#     id = models.IntegerField()
    environment_id = models.ForeignKey(Environments, db_column='environment_id')

    class Meta:
        managed = False
        db_table = 'suspend_activity'

    def __str__(self):  
        return ('%s_%s_%s' %(str(self.suspender), str(self.environment_id), str(self.suspend)))


class Team(models.Model):
    name =  models.CharField(max_length=50)
    email = models.EmailField(blank=True) 
    jiraTeamName = models.CharField(max_length=50,default='', blank=True) 
    class Meta:
        db_table = 'team'
        
    def __str__(self):  
        return self.name
    
class Features(models.Model):
    NAME,TEAM_ID,FIELD_ID,SERVER_ID=('name','team_id','field_id','server_id')
    name = models.CharField(max_length=50)
    team_id = models.ForeignKey(Team, db_column='team_id')
    field_id = models.ForeignKey(Fields, db_column='field_id')
    server_id = models.ForeignKey(Servers, db_column='server_id',null=True, blank=True, default = None)
    ignore_server = models.BooleanField(default = True);
    class Meta:
        db_table = 'features'
    def __str__(self):  
        return ('%s' %(str(self.name)))