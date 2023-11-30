from django.contrib import admin
from django.conf import settings
from apps.healthcheck.models import IndividualServer, Vip, Operation, Service, Environment, WebServiceType, LdapGroup, Team, RunResult, RunStatus, Environment
from apps.healthcheck.util.mail_util import sendMail
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from django.contrib import messages
from common_utils.django_util import Django_Util
from guardian.models import GroupObjectPermission,UserObjectPermission
from guardian.admin import GuardedModelAdmin
from common_utils.ldap_util import LdapUtil
from django.contrib.auth.models import User
from apps.ConfigModifier import models as config_models

# Register your models here.
class EnvironmentAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    
class VipAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('displayName',)
    list_display = ('displayName','vipName')
    search_fields = ['displayName','vipName']
    
class LdapGroupAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',) 
    def save_model(self, request, obj, form, change):
        try:
            if change:
                if 'auth_groups' in form.cleaned_data:
                    removing_groups = []
                    for group in obj.auth_groups.all():
                        if group not in  form.cleaned_data['auth_groups']: # means this group is removed
                            removing_groups.append(group)
                    if removing_groups:
                        user_name_list = LdapUtil.getGroupUserNames(obj.name)
                        for user_name in user_name_list:
                            if User.objects.filter(username=user_name).exists():
                                user = User.objects.get(username=user_name)
                                for group in removing_groups:
                                    if group in user.groups.all():
                                        user.groups.remove(group)
            obj.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, ("Exception was caught when save LdapGroup exception: %s." %(str(e)))) 
        
                
class IndividualServerAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'ipAddress', 'vip', 'environment')
    list_filter = ('vip', 'environment')
    search_fields = ['vip__displayName', 'environment__name', 'name', 'ipAddress']

class OperationAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('service', 'name', 'vip', 'environment', 'webservicetype')
    list_display = ('service', 'name', 'vip', 'environment', 'webservicetype', 'team', 'timeout')
    list_filter = ('service', 'vip', 'environment', 'webservicetype', 'team')
    search_fields = ['name','service__name', 'environment__name', 'vip__vipName', 'webservicetype__name', 'team__name']
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
         
        action = ""
        if change: # meaning it is new operation
            action = "changed"
        else:
            action = "added"
         
        if obj.environment.name == 'Production':
            sender = getattr(settings, "SENDER")
            toaddr = [obj.team.email]
            recipients = getattr(settings, "MODERATOR_EMAILS")
            application_url = getattr(settings, "APPLICATION_URL") + '/admin'
            message = """\
                <html>
                  <head></head>
                  <body>
                    <h3>API Healtcheck Monitor System</h3>
                    <p>
                        user <b>{0}</b> has <b>{1}</b> {2} operation for {3} in Production Environment under <b>{4}</b> team
                        <ul>
                            <li>Service Name: {5}</li>
                            <li>Service Endpoint: {6}</li>
                            <li>VIP: {7}</li>
                            <li>Team: {8}</li>
                        </ul>
                        <br>
                        Login to <a href="{9}">Healthcheck Application</a> to view request message
                    </p>
                  </body>
                </html>
            """.format(obj.user, action, obj.name, obj.service.name,  obj.team.name, obj.service.name, obj.service.endpoint, obj.vip.displayName, obj.team.name, application_url)
            sendMail(sender, toaddr, recipients, "API Healthcheck Monitor Alert", message)
         
        obj.save()
    
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
        if endpoint:
            existing_set = type(obj).objects.exclude(endpoint__isnull=True).filter(endpoint__iexact=endpoint)
            if len(existing_set) != 0 :
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
    
class TeamGuardedAdmin(GuardedModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'email', 'jiraTeamName')
    list_filter = ('name',)
    search_fields = ['name', 'email']   
    def save_model(self, request, obj, form, change):
        try:
            config_team = None
            if config_models.Team.objects.filter(name=obj.name).exists():
                config_team = config_models.Team.objects.get(name=obj.name)
            else:
                config_team = config_models.Team(name=obj.name)
            if change:
                config_team.name = form.cleaned_data[Team.NAME]
                config_team.email = form.cleaned_data[Team.EMAIL]
                config_team.jiraTeamName = form.cleaned_data[Team.JIRA_TEAM_NAME]     
                
                if Team.LDAP_GROUPS in form.cleaned_data and Team.USERS in form.cleaned_data:
                    for ldap_group in obj.ldap_groups.all():
                        if ldap_group not in  form.cleaned_data[Team.LDAP_GROUPS]: # means this group is removed
                            user_name_list = LdapUtil.getGroupUserNames(ldap_group.name)
                            obj_users = obj.users.all()
                            for user in obj.users.all():
                                if user.username in user_name_list:
                                    obj_users = obj_users.exclude(username=user.username)
                            form.cleaned_data[Team.USERS] = obj_users
     
            else:
                if Team.objects.filter(name=obj.name).exists():
                    messages.add_message(request, messages.ERROR, ("Team with same name %s already exists." %(str(obj.name)))) 
                    return
                config_team.name = obj.name
                config_team.email = obj.email
                config_team.jiraTeamName = obj.jiraTeamName
            config_team.save() 
            obj.save()
        except Exception as e:
            messages.add_message(request, messages.ERROR, ("Exception was caught when save Team exception: %s." %(str(e)))) 
    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        try:        
            for config_team in config_models.Team.objects.filter(name=obj.name):
                config_team.delete()
            obj.delete()
        except Exception as e:
            messages.add_message(request, messages.ERROR, ("Exception was caught when delete Team exception: %s." %(str(e)))) 
    def delete_selected(self, request, obj):
        for o in obj.all():
            self.delete_model(request,o)
class RunResultAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
class RunStatusAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    ordering = ('name',)
    
admin.site.register(IndividualServer, IndividualServerAdmin)
admin.site.register(Vip, VipAdmin)
admin.site.register(Operation, OperationAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(WebServiceType, WebServiceTypeAdmin)
admin.site.register(LdapGroup, LdapGroupAdmin)
# admin.site.register(Team, TeamAdmin)
admin.site.register(Team, TeamGuardedAdmin)
admin.site.register(RunResult, RunResultAdmin)
admin.site.register(RunStatus, RunStatusAdmin)
admin.site.register(GroupObjectPermission)
admin.site.register(UserObjectPermission)