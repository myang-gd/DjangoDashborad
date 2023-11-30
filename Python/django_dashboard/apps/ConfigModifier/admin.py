from django.contrib import admin
from apps.ConfigModifier import models
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from guardian.admin import GuardedModelAdmin
from common_utils.django_util import Django_Util
from django.contrib import messages

class FilemapAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('filename',)
    list_display = ('id', 'filename', 'server_type', 'location')
    list_filter = ('server_type',)
    search_fields = ['server_type__server_type', 'filename', 'location']
     
class FieldsAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'display', 'element_path', 'attribute', 'namespace', 'file_id', 'priority')
    list_filter = ('file_id', 'priority', "file_id__server_type",)
    search_fields = ['id','display', 'element_path', 'namespace', 'file_id__filename', 'file_id__location', 'priority__name', 'parent_id']

class FieldParamsAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display = ('id','param', 'value', 'field_id')
    list_filter = ('field_id',)
    search_fields = ['param', 'value', 'field_id__display']
     
class FieldValuesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display = ('id','field_value', 'field_id')
    list_filter = ('field_id',)
    search_fields = ['field_value', 'field_id__display']

class FieldsStatusAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'enabled', 'environment_id', 'field_id', 'warnings', 'server_id')
    list_filter = ('field_id','environment_id')
    search_fields = ['environment_id__environment', 'field_id__display', 'warnings']
    
class ServersAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display = [field.name for field in models.Servers._meta.fields]
    list_filter = ('environment_id','server_type')
    search_fields = ['server_name','server_type__project__name','server_type__server_tier__name']
    def save_model(self, request, obj, form, change):
        message = '';
        server_name = Django_Util.getField(obj, 'server_name')
        if not change : # meaning it is new operation
            existing_set = type(obj).objects.filter(server_name__iexact=server_name)
            if len(existing_set) != 0 :
                message += 'Server with the same name already exist!!!'
                messages.set_level(request, messages.WARNING)
                messages.error(request, message)
                return False
        obj.save()
class CurrentLocksAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.CurrentLocks._meta.fields]
    list_filter = ('user_id','environment_id','is_active','is_complete','is_cancelled','server_id','field_id')
    search_fields = ['id', 'duration', 'user_id__login','field_id__display']
class EnvironmentsAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.Environments._meta.fields]
    list_filter = ('enabled',)
    search_fields = ['environment']
class FieldDefaultMapAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.FieldDefaultMap._meta.fields]
    list_filter = ('environment_id','field_id','server_id')
    search_fields = ['default_value']
class ServerTypesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    list_display =  [field.name for field in models.ServerTypes._meta.fields]
    search_fields = ['project__name', 'server_tier__name']
    def save_model(self, request, obj, form, change):
        message = '';
        project = Django_Util.getField(obj, 'project')
        server_tier = Django_Util.getField(obj, 'server_tier')
        is_cloud = Django_Util.getField(obj, 'is_cloud')
        existing_set = type(obj).objects.filter(project=project, server_tier=server_tier, is_cloud=is_cloud)
        if len(existing_set) != 0 :
            message += 'Following services with the same project/server_tier/is_cloud already exist: ' + str(project) + "/" + str(server_tier) + "/" + str(is_cloud)
            messages.set_level(request, messages.WARNING)
            messages.error(request, message)
            return False
        obj.save()
class FieldValidationsAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.FieldValidations._meta.fields]
    list_filter = ('field_id','type')
    search_fields = ['validation']
class FilemapStatusAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.FilemapStatus._meta.fields]
    list_filter = ('environment_id','filemap_id',)
class GdUserAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.GdUser._meta.fields]
    list_filter = ('empowered','cm')
    search_fields = ['login']
class SuspendActivityAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.SuspendActivity._meta.fields]
    list_filter = ('suspend','suspender', 'environment_id')
    search_fields = ['suspender__login']
class ValidationTypesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.ValidationTypes._meta.fields]
    search_fields = ['type']

class TeamGuardedAdmin(GuardedModelAdmin): 
    ordering = ('name',)
    list_display = ('name', 'email', 'jiraTeamName')
    list_filter = ('name',)
    search_fields = ['name', 'email']  
class FeaturesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.Features._meta.fields]
    search_fields = ['name']
class PriorityAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.Priority._meta.fields]
    search_fields = ['name']
class ValueTypesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.ValueTypes._meta.fields]
    search_fields = ['value_type']
class FileTypesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.FileTypes._meta.fields]
    search_fields = ['file_type']
class ProjectAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.Project._meta.fields]
    search_fields = ['name']
class ServerTierAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.ServerTier._meta.fields]
    search_fields = ['id']
class LockActionAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.LockAction._meta.fields]
    search_fields = ['id','action']
class LockStatesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.LockStates._meta.fields]
    search_fields = ['id','status_type','description']
class FilemapTraceAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('id',)
    list_display =  [field.name for field in models.FilemapTrace._meta.fields]
    search_fields = ['id','filemap_id__location','filemap_id__filename','filemap_id__server_type__project__name','filemap_id__server_type__server_tier__name']
     
admin.site.register(models.Filemap, FilemapAdmin)
admin.site.register(models.Fields, FieldsAdmin)
admin.site.register(models.FieldParams, FieldParamsAdmin)
admin.site.register(models.FieldValues, FieldValuesAdmin)
admin.site.register(models.FieldsStatus, FieldsStatusAdmin)
admin.site.register(models.Servers, ServersAdmin)
admin.site.register(models.CurrentLocks, CurrentLocksAdmin)
admin.site.register(models.Environments, EnvironmentsAdmin)
admin.site.register(models.FieldDefaultMap, FieldDefaultMapAdmin)
admin.site.register(models.FieldValidations, FieldValidationsAdmin)
admin.site.register(models.FilemapStatus, FilemapStatusAdmin)
admin.site.register(models.GdUser, GdUserAdmin)
admin.site.register(models.SuspendActivity, SuspendActivityAdmin)
admin.site.register(models.ServerTypes, ServerTypesAdmin)
admin.site.register(models.ValidationTypes, ValidationTypesAdmin)
admin.site.register(models.Team, TeamGuardedAdmin)
admin.site.register(models.Features, FeaturesAdmin)
admin.site.register(models.Priority, PriorityAdmin)
admin.site.register(models.ValueTypes, ValueTypesAdmin)
admin.site.register(models.FileTypes, FileTypesAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ServerTier, ServerTierAdmin)
admin.site.register(models.LockAction, LockActionAdmin)
admin.site.register(models.LockStates, LockStatesAdmin)
admin.site.register(models.FilemapTrace, FilemapTraceAdmin)


      
