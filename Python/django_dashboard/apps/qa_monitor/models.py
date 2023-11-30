from django.db import models
from django.contrib.auth.models import User
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class Environment(models.Model):
    NONE = 'None'
    name =  models.CharField(max_length=50)
    
    def __str__(self):  
        return self.name
    
    class Meta:
        db_table = "Environment"
    
        
class RunStatus(models.Model):
    
    CANCELED = 'Canceled'
    RUNNING = 'Running'
    FINISHED = 'Finished'
    
    name = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
    class Meta:
        db_table = "RunStatus"

class RunResult(models.Model):
    
    NA = 'N/A'
    PASS = 'Pass'
    FAIL = 'Fail'
    
    name = models.CharField(max_length=10)   

    def __str__(self):
        return self.name
    class Meta:
        db_table = "RunResult"
        
class MonitorType(models.Model):
    
    TSYS_QUEUE = 'TSYS_QUEUE'
    PAL = 'PAL'
    PIN_GRABBER = 'PIN_GRABBER'
    
    MONITOR_TYPES = (
        (TSYS_QUEUE, 'Tsys Queue'), 
        (PAL, 'Pal'),
        (PIN_GRABBER, 'Pin Grabber'),                 
    )

    type = models.CharField(max_length=255, choices=MONITOR_TYPES, default=TSYS_QUEUE)
    
    def __str__(self):
        return self.type
    
    class Meta:
        db_table = "MonitorType"
        
class Processor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    processMethod = models.CharField(max_length=180, blank=True, default='')
    model = models.CharField(max_length=50, blank=True, default='')
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

class IndividualServer(models.Model):
    name  = models.CharField(max_length=50, unique=True)
    ipAddress = models.CharField(max_length=50)
    vip = models.ForeignKey(Vip, null=True, blank=True)
    environment = models.ForeignKey(Environment, null=True, blank=True)
      
    def __str__(self):
        return self.name
    
class MonitorSchedule(models.Model):
    name =  models.CharField(max_length=50) 
    description =  models.CharField(max_length=500, null=True, blank=True)
    recipient_list =  models.CharField(max_length=500, null=True, blank=True)
    environment = models.ForeignKey(Environment)
    processor = models.ForeignKey(Processor, null=True)
    operation_id = models.CharField(max_length=50, null=True, blank=True)
    owner_id = models.IntegerField(null=True)
    periodic_task_id = models.IntegerField(null=True)
    skip_success = models.BooleanField(_('skip successful result'), default=False)
    store_result = models.BooleanField(_('store result in data base'), default=False)
    latest_result = models.ForeignKey(RunResult, null=True)
    server = models.ForeignKey(IndividualServer, db_column='server', null=True, blank=True)
    email_title =  models.CharField(max_length=200, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.latest_result is None:  
            self.latest_result = RunResult.objects.get(name=RunResult.NA)
        super(MonitorSchedule, self).save(*args, **kwargs)
    def get_owner(self):
        if self.owner_id:
            try:
                owner = User.objects.get(id=self.owner_id)
            except:
                return None
            else:
                return owner
    def set_owner(self, userobj):
        if userobj:
            try:
                user_id = userobj.id
                self.owner_id = user_id
                self.save()
            except:
                pass
    def get_periodic_task(self):
        if self.periodic_task_id:
            try:
                periodic_task = PeriodicTask.objects.get(id=self.periodic_task_id)
            except:
                return None
            else:
                return periodic_task
    def set_periodic_task(self, periodic_task_obj):
        if periodic_task_obj:
            try:
                periodic_task_id = periodic_task_obj.id
                self.periodic_task_id = periodic_task_id
                self.save()
            except:
                pass
    def schedule_edit_every(self, name, task_name,  enabled, interval_schedule_id, crontab_schedule_id, args=None, kwargs=None, sameName=True):
        crontab_schedule = None
        interval_schedule = None
        if interval_schedule_id and IntervalSchedule.objects.filter(id=interval_schedule_id).exists():
            interval_schedule = IntervalSchedule.objects.get(id=interval_schedule_id)
        if crontab_schedule_id and CrontabSchedule.objects.filter(id=crontab_schedule_id).exists():
            crontab_schedule = CrontabSchedule.objects.get(id=crontab_schedule_id)
            
        if self.periodic_task_id:
            ptask = PeriodicTask.objects.get(id=self.periodic_task_id)  
            ptask.interval = interval_schedule
            ptask.crontab =  crontab_schedule
        else:
            ptask = PeriodicTask(name=name, task=task_name, interval=interval_schedule, crontab=crontab_schedule) 
            ptask.save()
            self.periodic_task_id = ptask.id
            self.save()
        if name is not None and name != "":
            if sameName: 
                self.name = name
            ptask.name = name
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        if type(enabled) == type(True):
            ptask.enabled = enabled
        ptask.save()
        self.save()
        
    def stop(self):
        """pauses the task"""
        if self.periodic_task_id:
            ptask = PeriodicTask.objects.get(id=self.periodic_task_id)
            ptask.enabled = False
            ptask.save()

    def start(self):
        """starts the task"""
        if self.periodic_task_id:
            ptask = PeriodicTask.objects.get(id=self.periodic_task_id)
            ptask.enabled = True
            ptask.save()

    def terminate(self):
        self.stop()
        if self.periodic_task_id:
            ptask = PeriodicTask.objects.get(id=self.periodic_task_id)
            self.delete()
            ptask.delete()
    
    def __str__(self):
        return self.name   
    def name_env(self): 
        if self.environment.name == Environment.NONE:
            return self.name
        else: 
            return ('%s (%s)' %(self.name, (self.environment.name if self.environment else "N/A")))
    class Meta:
        db_table = "MonitorSchedule"
class Run(models.Model):
    name =  models.CharField(max_length=50, null=True, blank=True) 
    startDate = models.DateTimeField(blank=True,default=timezone.now)
    schedule = models.ForeignKey(MonitorSchedule, null=True)
    status = models.ForeignKey(RunStatus, null=True) 
    result = models.ForeignKey(RunResult, null=True) 
    def __str__(self):
        return self.name  
class OperationRun(models.Model):
    startDate = models.DateTimeField(default=timezone.now)
    run = models.ForeignKey(Run, null=True)
    result = models.ForeignKey(RunResult, null=True) 
    responseMessage = models.TextField(null=True, blank=True)
    validationResult = models.TextField(null=True, blank=True)  

class WebServiceType(models.Model):
    SOAP = 'SOAP'
    REST = 'REST'
    name = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
   
class Service(models.Model):
    name = models.CharField(max_length=50, unique=True)
    endpoint = models.CharField(max_length=180)
    port = models.CharField(max_length=120, blank=True, default='')
    key = models.CharField(max_length=120, blank=True, default='')
    cert = models.CharField(max_length=120, blank=True, default='')
    class Meta:
        permissions = (
            ("import", "Can import from file"),
            ("export", "Can export to file"),
        )
    def __str__(self):
        return self.name

class Team(models.Model):
    name =  models.CharField(max_length=50)
    email = models.EmailField(blank=True) 
    jiraTeamName = models.CharField(max_length=50,default='', blank=True) 
    def __str__(self):  
        return self.name
class OperationType(models.Model):
    PTS = 'PTS'
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
class Method(models.Model):
    POST,GET = ('post','get')
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
class MessageType(models.Model):
    XML,JSON = ('xml', 'json')
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
class ValidationType(models.Model):
    REGEX,PLAIN = ('regex','plain')
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
    vip = models.ForeignKey(Vip, null=True, blank=True)
    service = models.ForeignKey(Service, null=True, blank=True)
    environment=models.ForeignKey(Environment, null=True, blank=True)
    webservicetype=models.ForeignKey(WebServiceType)
    operationType=models.ForeignKey(OperationType,null=True, blank=True)
    team=models.ForeignKey(Team)
    jiraTicket=models.CharField(max_length=50, default='', blank=True)
    method=models.ForeignKey(Method, null=True, blank=True)
    messageType=models.ForeignKey(MessageType, null=True, blank=True)
    validationType=models.ForeignKey(ValidationType, null=True, blank=True)
    class Meta:
        permissions = (
            ("import", "Can import from file"),
            ("export", "Can export to file"),
        )
    def __str__(self):
        return self.name + "_" + str(self.environment) + "_" + str(self.service) 
    def request_msg(self):
        return self.requestMessage


class SqlConn(models.Model):
    name = models.CharField(max_length=50)
    server = models.CharField(max_length=50, blank=True, default='')
    db = models.CharField(max_length=50, blank=True, default='')
    user = models.CharField(max_length=50, blank=True, default='')
    pwd =  models.CharField(max_length=50, blank=True, default='')
    environment = models.ForeignKey(Environment,null=True, blank=True)
    def __str__(self):
        return self.name + "_" + str(self.environment)
    def getConnectionStr(self):
        return ("Server: %s, Database: %s" % (str(self.server), str(self.db)))
class SqlQuery(models.Model):
    name = models.CharField(max_length=50)
    sqlconn = models.ForeignKey(SqlConn)
    environment = models.ForeignKey(Environment, null=True, blank=True)
    query = models.TextField()
    validations = models.TextField()
    def __str__(self):
        return self.name + "_" + str(self.environment)
    def request_msg(self):
        return self.query
class Cmd(models.Model):
    name = models.CharField(max_length=50)
    script = models.TextField()
    validations = models.TextField()
    environment = models.ForeignKey(Environment, null=True, blank=True)
    def __str__(self):
        return self.name + "_" + str(self.environment)
    def request_msg(self):
        return self.script
class FWAccount(models.Model):
    identifier = models.CharField(max_length=50)
    createDate = models.DateTimeField(blank=True,default=timezone.now)
    def __str__(self):
        return self.identifier