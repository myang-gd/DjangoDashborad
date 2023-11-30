from django.contrib import admin
from apps.qa_monitor.models import Environment, Cmd, Service, WebServiceType, Team, RunResult, RunStatus, Vip, IndividualServer, Operation, SqlConn, SqlQuery, Processor, Method
from apps.qa_monitor import models
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from django.contrib import messages
from common_utils.django_util import Django_Util
# Register your models here.
class EnvironmentAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    
class VipAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('displayName',)
    list_display = ('displayName','vipName')
    search_fields = ['displayName','vipName']
class CmdAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',) 

class SqlConnAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class SqlQueryAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class ProcessorAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',) 
    
class IndividualServerAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'ipAddress', 'vip', 'environment')
    list_filter = ('vip', 'environment')
    search_fields = ['vip__displayName', 'environment__name', 'name', 'ipAddress']
 
class OperationAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('service', 'name', 'vip', 'environment', 'webservicetype')
    list_display = ('service', 'name', 'vip', 'environment', 'webservicetype', 'team')
    list_filter = ('service', 'vip', 'environment', 'webservicetype', 'team')
    search_fields = ['name','service__name', 'environment__name', 'vip__vipName', 'webservicetype__name', 'team__name']
        
    class Media:
        js = ['/static/js/action_change.js', '/static/js/operation_save_check.js']
         
class ServiceAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'endpoint', 'port')
    list_filter = ('endpoint',)
    search_fields = ['name', 'endpoint']
    def save_model(self, request, obj, form, change):
        message = '';
        endpoint = Django_Util.getField(obj, 'endpoint')
        port = Django_Util.getField(obj, 'port')
        if endpoint:
            existing_set = type(obj).objects.exclude(endpoint__isnull=True).filter(endpoint__iexact=endpoint, port__iexact=port)
            if (len(existing_set) != 0 and not change) or (len(existing_set) > 1 and change):
                message += 'Following services with the same endpoint already exist: '
                for sevice in existing_set:
                    name = Django_Util.getField(sevice, 'name') 
                    message += str(name) + ", "
                messages.set_level(request, messages.WARNING)
                messages.error(request, message)
                return False
        obj.save()
class WebServiceTypeAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    list_display = ('name',)
 
class TeamAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'email', 'jiraTeamName')
    list_filter = ('name',)
    search_fields = ['name', 'email']
     
class RunResultAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class RunStatusAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class MethodAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class MessageTypeAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class ValidationTypeAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)

admin.site.register(IndividualServer, IndividualServerAdmin)
admin.site.register(Vip, VipAdmin)
admin.site.register(Operation, OperationAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(WebServiceType, WebServiceTypeAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(RunResult, RunResultAdmin)
admin.site.register(RunStatus, RunStatusAdmin)
admin.site.register(Cmd, CmdAdmin)
admin.site.register(SqlConn, SqlConnAdmin)
admin.site.register(SqlQuery, SqlQueryAdmin)
admin.site.register(Processor, ProcessorAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(models.MessageType, MessageTypeAdmin)
admin.site.register(models.ValidationType, ValidationTypeAdmin)