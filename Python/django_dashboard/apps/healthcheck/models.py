from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext as _
from audit_log.models.managers import AuditLog
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.utils import timezone
# Create your models here.

class Environment(models.Model):
    name =  models.CharField(max_length=50)
    
    def __str__(self):  
        return self.name


class Vip(models.Model):
    COM = 'necla'
    SOACOM = 'gdcsvc'
    V3 = 'gdcsvcv3'
    displayName =  models.CharField(max_length=50)
    vipName  = models.CharField(max_length=50)
    
    def __str__(self):  
        return self.displayName

class WebServiceType(models.Model):
    SOAP = 'SOAP'
    REST = 'REST'
    name = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name

class IndividualServer(models.Model):
    name  = models.CharField(max_length=50, unique=True)
    ipAddress = models.CharField(max_length=50)
    vip = models.ForeignKey(Vip)
    environment = models.ForeignKey(Environment)
    
    def __str__(self):
        return self.name
    
class Service(models.Model):
    name = models.CharField(max_length=50, unique=True)
    endpoint = models.CharField(max_length=180)
    port = models.CharField(max_length=120, blank=True, default='')
    key = models.CharField(max_length=120, blank=True, default='')
    cert = models.CharField(max_length=120, blank=True, default='')
    audit_log = AuditLog()
    class Meta:
        permissions = (
            ("import", "Can import from file"),
            ("export", "Can export to file"),
        )
    def __str__(self):
        return self.name

class LdapGroup(models.Model):
    name =  models.CharField(max_length=50)
    auth_groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
    )
    class Meta:
        verbose_name = _('ldap_group')
        verbose_name_plural = _('ldap_groups')
    def __str__(self):  
        return self.name

class Team(models.Model):    
    CHANGE_FEATURE,DELETE_FEATURE,ADD_FEATURE=  ('change_feature','delete_feature','add_feature')
    CANCEL_CONFIG = 'cancel_team_config_request'
    NAME,EMAIL,JIRA_TEAM_NAME,LDAP_GROUPS,USERS=('name','email','jiraTeamName','ldap_groups','users')
    
    name =  models.CharField(max_length=50)
    email = models.EmailField(blank=True) 
    jiraTeamName = models.CharField(max_length=50,default='', blank=True) 
    ldap_groups = models.ManyToManyField(
        LdapGroup,
        verbose_name=_('ldap_groups'),
        blank=True,
    )
    users = models.ManyToManyField(
        User,
        verbose_name=_('users'),
        blank=True,
    )
    def __str__(self):  
        return self.name
    
class OperationType(models.Model):
    PTS = 'PTS'
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name    
    
class Operation(models.Model):
    name = models.CharField(max_length=50)
    requestMessage = models.TextField()
    username = models.CharField(max_length=50, default='', blank=True)
    password = models.CharField(max_length=50, default='', blank=True)
    validations = models.TextField()
    headers = models.TextField(max_length=500, default='', blank=True)
    vip = models.ForeignKey(Vip)
    service = models.ForeignKey(Service)
    environment=models.ForeignKey(Environment)
    webservicetype=models.ForeignKey(WebServiceType)
    operationType=models.ForeignKey(OperationType,null=True, blank=True)
    team=models.ForeignKey(Team)
    jiraTicket=models.CharField(max_length=50, default='', blank=True)
    audit_log = AuditLog()
    timeout = models.PositiveIntegerField(blank=True, null=True)
    class Meta:
        permissions = (
            ("import", "Can import from file"),
            ("export", "Can export to file"),
        )
    def __str__(self):
        return self.name

class ResponseAuditLogEntry(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    time = models.TimeField()
    service = models.ForeignKey(Service)
    operation = models.ForeignKey(Operation)
    responseMessage = models.TextField()
    validationResult = models.TextField(default='')
    
class RunStatus(models.Model):
    CANCELED = 'Canceled'
    RUNNING = 'Running'
    FINISHED = 'Finished'
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name
class RunResult(models.Model):
    NA = 'N/A'
    PASS = 'Pass'
    FAIL = 'Fail'
    name = models.CharField(max_length=10)   
    def __str__(self):
        return self.name
class Schedule(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True, unique=True) 
    description =  models.CharField(max_length=500, null=True, blank=True)
    periodically_run =   models.CharField(max_length=30, null=True, blank=True) 
    environment = models.ForeignKey(Environment, null=True)
    owner = models.ForeignKey(User, null=True)
    description =  models.CharField(max_length=500, null=True, blank=True)
    periodic_task = models.ForeignKey(PeriodicTask, null=True)
    threshold =  models.PositiveIntegerField(default=100, blank=True, null=True)
    enable_run_log = models.NullBooleanField(default=False, blank=True)
    def schedule_edit_every(self, name, task_name,  enabled, interval_schedule_id, crontab_schedule_id, args=None, kwargs=None):
        crontab_schedule = None
        interval_schedule = None        
        if interval_schedule_id and IntervalSchedule.objects.filter(id=interval_schedule_id).exists():
            interval_schedule = IntervalSchedule.objects.get(id=interval_schedule_id)
        if crontab_schedule_id and CrontabSchedule.objects.filter(id=crontab_schedule_id).exists():
            crontab_schedule = CrontabSchedule.objects.get(id=crontab_schedule_id)
            
        if self.periodic_task:
            ptask = self.periodic_task  
            ptask.interval = interval_schedule
            ptask.crontab =  crontab_schedule
        else:
            ptask = PeriodicTask(name=name, task=task_name, interval=interval_schedule, crontab=crontab_schedule) 
            ptask.save()
        if name is not None and name != "":
            self.name = name
            ptask.name = name
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        if type(enabled) == type(True):
            ptask.enabled = enabled
        ptask.save()
        self.periodic_task = ptask
        self.save()
        
    def stop(self):
        """pauses the task"""
        ptask = self.periodic_task
        if ptask: 
            ptask.enabled = False
            ptask.save()

    def start(self):
        """starts the task"""
        ptask = self.periodic_task
        ptask.enabled = True
        ptask.save()

    def terminate(self):
        self.stop()
        ptask = self.periodic_task
        self.delete()
        if ptask:
            ptask.delete()
    def __str__(self):
        return self.name 
class Run(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True) 
    startDate = models.DateTimeField(blank=True,default=timezone.now)
    schedule = models.ForeignKey(Schedule, null=True)
    owner = models.ForeignKey(User, null=True)
    status = models.ForeignKey(RunStatus, null=True) 
    result = models.ForeignKey(RunResult, null=True) 
    needCancel = models.BooleanField(default=False)  
    def __str__(self):
        return self.name  
class OperationRun(models.Model):
    startDate = models.DateTimeField(default=timezone.now)
    run = models.ForeignKey(Run, null=True)
    service = models.ForeignKey(Service, null=True)
    operation = models.ForeignKey(Operation, null=True)
    result = models.ForeignKey(RunResult, null=True) 
    responseMessage = models.TextField(null=True, blank=True)
    validationResult = models.TextField(null=True, blank=True)  
    elapsed = models.FloatField(blank=True, null=True)