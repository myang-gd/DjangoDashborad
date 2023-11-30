from django.http import HttpResponse
from . import models
from . import forms 
from django.shortcuts import render
from django.forms import formset_factory
from django.contrib import messages
from django.http import HttpResponseRedirect
from contextlib import contextmanager
from common_utils.xml_util import XmlUtil
from common_utils.json_util import JsonUtil
from common_utils.django_util import Django_Util
from common_utils.io_util import FileUtil
from .dto.configEntry import EntryAddResult
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import re
import json
import logging
import traceback
from django.forms.models import model_to_dict
from collections import OrderedDict
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from apps.healthcheck import models as default_models
from django.db.models import Q
from apps.ConfigModifier.models import FileTypes
from django.core.exceptions import PermissionDenied

CONFIGMODIFIER = 'configModifier'
CONFIGMODIFIER_ENTRYSELECT = 'configModifier_entrySelect'
CONFIGMODIFIER_ENTRYADD = 'configModifier_entryAdd'
CONFIGMODIFIER_ENTRYRESULT = 'configModifier_entryResult'
CONFIGMODIFIER_MAKEREQUEST = 'configModifier_makeRequest'
CONFIGMODIFIER_TEAM = 'configModifier_team'
CONFIGMODIFIER_FEATURE = 'configModifier_feature'
CONFIGMODIFIER_AJAX = 'configModifier_ajax'
CONFIGMODIFIER_REQUEST = 'configModifier_request'
CONFIGMODIFIER_CM = 'configModifier_cm'

K_FORM,K_FORMSET,K_COMMON_FORM,K_FEATURE_FORM = ('form','formset','CommonForm','featureForm')
K_NODE_TYPE_ADD,K_ENABLE_PARENT,K_IS_PREVIEW = ('node_type_add','enableParent','isPreview')
K_RESULT_LIST = 'resultList'
K_ENTRY_RESULT_MAP = 'entryResultMap'
K_HELP_LINK = "help_link"

FILE_MAP, FIELD_PARAM, FIELD_VALUE, FIELD = (
    'file_map', 'field_param', 'field_value', 'field'
)
PREVIEW, SUBMIT = ('preview', 'submit')
YES, NO = ('Yes', 'No')
PREVIEW_XML = 'preview_xml'
INNER_TEXT, INNER_XML = ('InnerText', 'InnerXml')
BLOCK_SUBMIT = 'block_submit'

ENV_ID, STP_ID, SERVER_ID, FILE_ID, CONFIG_ID, TEAM_ID, FEATURE_ID, ACTION_ID, VALUE_ID, VALUE_TYPE_ID =  (
    'environment_id', 'server_type_id', 'server_id','file_id', 'config_id', 'team_id','feature_id','action_id','value_id','value_type_id'
)
ID = 'id'
SUBMIT_TYPE = 'submit_type' 
ERROR = 'error'
VALUE = 'value'
EDIT,DEL,CNL = ('edit','delete','cancel')
SUSPEND,UNSUSPEND,ADD_VALUE,CHANGE_VALUE, GET_VALUE_TYPE, CHECK = ('1','2','add_value','change_value', 'get_value_type', "check")
ENV_STATUS_LIST,ENVIRONMENT_LIST,VALUE_LIST,SERVER_LIST,FILE_LIST,CONFIG_LIST,FEATURE_LIST= ('env_status_list','environment_list','value_list','server_list',
                                                                                             'file_list','config_list','feature_list')

APP_JSON = 'application/json'
HAS_SAME_SERVER_TYPE, SERVER_NAMES, PRIORITY, INCLUDE_ALL_SERVERS = ('has_same_server_type','server_names','priority','include_all_servers')

HOME_HELP_URL = "https://confluence/display/QAAR/Config+Modifier+Tool+-+Portal"
SHOW_VALUE_TYPE = "show_value_type"
def configModifier(request, template="overview.html"):
    size = 200
    all_currentLocks = models.CurrentLocks.objects.prefetch_related('user_id','field_id','environment_id','field_id__priority')
    active_list = all_currentLocks.filter(is_active=True).order_by('-requesttime')[:size]
    pending_list = all_currentLocks.filter(is_active=False, is_complete=False, is_cancelled=False).order_by('-requesttime')[:size]
    completed_list = all_currentLocks.filter(is_complete=True).order_by('-requesttime')[:size]
    cancelled_list = all_currentLocks.filter(is_active=False, is_complete=False, is_cancelled=True).order_by('-requesttime')[:size]

    list_map = OrderedDict() 
    list_map['active_requests'] = {'list': getCurrentLocksFieldList(active_list, request),'title':'Active requests'}
    list_map['pending_requests'] = {'list': getCurrentLocksFieldList(pending_list, request) ,'title':'Pending requests'}
    list_map['completed_requests'] = {'list': getCurrentLocksFieldList(completed_list, request) ,'title':'Completed requests'}
    list_map['cancelled_requests'] = {'list': getCurrentLocksFieldList(cancelled_list, request) ,'title':'Cancelled requests'}
    return render(request, template, {'list_map':list_map, 'env_status_list':getEnvStatusList(), K_HELP_LINK: HOME_HELP_URL })

def request(request, pk, action, template="overview.html"):

    if request.method == 'GET':       
        if action == CNL:
            try:
                lock = models.CurrentLocks.objects.get(id=pk)
                if not lock.is_cancelled and not lock.is_complete:
                    if lock.is_active:   
                        lock.duration = 1                   
                    else:
                        lock.is_cancelled = True
                    
                    lock.save()
                    
                    if lock.is_active:            
                        messages.add_message(request, messages.INFO, ("Shortened duration to 1 minute for active request (Id = %s)." %(pk))) 
                    else:
                        messages.add_message(request, messages.INFO, ("Canceled pending request (Id = %s)." %(pk))) 
                         
            except Exception as e:
                messages.add_message(request, messages.ERROR, "Exception was caught when cancel lock request, Exception: " + str(e))                 
            
    return HttpResponseRedirect(reverse(CONFIGMODIFIER))

def getFiledDelay(field_id=None, field_obj=None):    
    delay = 0 
    priority_str = models.Priority.NORMAL
    if field_obj:
        priority = field_obj.priority
    elif  models.Fields.objects.filter(id=field_id).exists():
        priority = models.Fields.objects.prefetch_related(models.Fields.PRIORITY).get(id=field_id).priority
    if priority:
        delay =  priority.delay
        priority_str = str(priority)
    return delay, priority_str

def getJsonFieldParaMapFromModel(field):
    field_para_map = {}
    error = ''
    if not models.FieldParams.objects.filter(field_id=field).exists():
        return field_para_map, error
    for field_para in models.FieldParams.objects.filter(field_id=field):
        try: 
            field_para_map[field_para.param] = json.loads(field_para.value)
        except Exception as e:
            if 'Expecting value' in str(e):
                field_para_map[field_para.param] = field_para.value
                continue
            else:
                error = 'failed to load string as json: [%s] due to error %s'  %(str(field_para.value), str(e))
    return field_para_map, error

def validateXmlEntriesByField(fields_list, networkpath):   
    is_accessible, fileBytes, return_msg = checkNetWorkPathAccessible(networkpath)
    file_content = ''
    if fileBytes:
        file_content =  fileBytes.decode('utf-8')
    if not is_accessible:
        result =  'Path: '+ networkpath + ' is not accessible or writable(RE-18432). message: ' + return_msg
        return is_accessible, file_content, result, 'N/A'
    index = ""
    xpath = r'//'
    has_default_namespace = False
    has_index = False
    i = 0
    for field in fields_list:
        has_index = False
        index = ""
        remove_field = field.remove_field
        remove_attribute = field.remove_attribute        
        if remove_field:
            continue;
        element_path = field.element_path
        attribute = field.attribute
        namespace =  field.namespace
        FieldParaMap = {}
        for field_para in models.FieldParams.objects.filter(field_id=field):
            FieldParaMap[field_para.param] = field_para.value
        index_match = re.search(r"(?P<index>\[(?!-)\d+(?<!-)\]?)", element_path, re.IGNORECASE)
        if index_match:
            index = index_match.group('index')
        if index:
            has_index = True
            element_path = element_path.replace(index, "")
        if has_index :
            xpath = "(" + xpath
               
        if namespace :
            has_default_namespace = True
            element_path = 'test:' + element_path

        if xpath.endswith(r'//'):
            xpath += element_path
        else:
            xpath += r'//' + element_path  
      
        if FieldParaMap:
            xpath += '[' 
        for key in FieldParaMap:
            xpath += (r"@%s='%s' and" % (key, FieldParaMap[key]))
        if xpath.endswith('and'):
            xpath = xpath[:-3]
        if FieldParaMap:
            xpath += ']' 
        if attribute and i == 0 and not remove_attribute and attribute != INNER_TEXT and attribute != INNER_XML:  # first form
            xpath += r'/@' + attribute
        
        if has_index :
            xpath +=  ")" + index
            
        if not attribute and i == 0 and not remove_field and not remove_attribute:
            return False, file_content, 'Attribute of xml leaf node can not be empty.', 'N/A'
        i += 1 
    if xpath == r'//':
        return True,file_content, ''     
    name_space_map = {"xsl":"http://www.w3.org/1999/XSL/Transform"}
    if has_default_namespace:
        name_space_map["test"] =  namespace
    result, is_found = XmlUtil.get_str_element_result_flag( fileBytes, xpath, name_space_map)    
    if not is_found:
        return False, file_content, 'Node does not exist xpath: ' + xpath,result, 'N/A'
    else:
        return True, file_content , '', result
def validateJsonEntriesByField(fields_list, networkpath):
    is_accessible, fileBytes, return_msg = checkNetWorkPathAccessible(networkpath)
    file_content = ''
    if fileBytes:
        file_content =  fileBytes.decode('utf-8') 
    if not is_accessible:
        result =  'Path: '+ networkpath + ' is not accessible or writable(RE-18432). message: ' + return_msg
        return is_accessible, file_content, result, 'N/A'
    index = ""
    has_index = False

    data = fileBytes.decode("utf-8")
    #remove BOM header
    if data.startswith(u'\ufeff'):
        data = data.encode('utf8')[3:].decode('utf8')
    i = 0   
    for field in fields_list:
        path = r'$..'
        has_index = False
        index = ""
        remove_field = field.remove_field     
        if remove_field:
            continue;
        element_path = field.element_path
        attribute = field.attribute       
        
        if element_path.startswith("."):
            path =  r'$.'
            element_path = element_path.replace(".","")  
               
        index_match = re.search(r"(?P<index>\[(?!-)\d+(?<!-)\]?)", element_path, re.IGNORECASE)
        if index_match:
            index = index_match.group('index')
        if index:
            has_index = True
            element_path = element_path.replace(index, "")
        if has_index :
            path += element_path + index
        else:
            FieldParaMap, error = getJsonFieldParaMapFromModel(field)
            if error:
                return False,file_content, error
            errorJsonMap = validJsonMap(FieldParaMap)
            if errorJsonMap:
                return False, file_content, errorJsonMap
            path += element_path
            if FieldParaMap:
                path += '[?(' 
                for key in FieldParaMap:
                    path += (r"@.%s == %s" % (key, getPathString(FieldParaMap[key])))
                    if list(FieldParaMap.keys())[-1] != key:
                        path += " && "
                path += ')]'
        if not attribute and i == 0:
            return False, file_content, 'Attribute of json leaf node can not be empty.', 'N/A'
        if attribute and i == 0: # means the leaf node
            path += ('' if path.endswith(".") else '.' )+ attribute
            
        result, is_found, error = JsonUtil.get_str_element_result_flag( data, path)  
        if not is_found:
            return False, file_content, ('Node does not exist path: %s, error: %s' % (path, error)), 'N/A'
        i += 1
    return True, file_content,'', result

def checkLockValueChangedAsRequest(lock_id):
    lock = models.CurrentLocks.objects.get(id=lock_id)
    server_name = lock.server_id.server_name
    file_map = lock.field_id.file_id
    path = '\\\\%s\\%s\\%s' % (server_name, file_map.location, file_map.filename)
    field_list = []
    current_field = lock.field_id
    field_list.append(current_field)
    while current_field.parent_id != None :
        current_field = models.Fields.objects.get(id=current_field.parent_id)
        field_list.append(current_field)
    if path.endswith('json'):
        result, content, message, current = validateJsonEntriesByField(field_list, path)
    else:
        result, content, message, current = validateXmlEntriesByField(field_list, path)
    
    is_changed_as_expect = False
    current = str(current)
    expect = str(lock.value)
    if current.upper() == expect.upper():
        is_changed_as_expect = True
    
    return is_changed_as_expect, current, expect
     
def checkLockStatus(lock_id, request):
    lock = models.CurrentLocks.objects.get(id=lock_id)
    server_name = lock.server_id.server_name
    file_map = lock.field_id.file_id
    path = '\\\\%s\\%s\\%s' % (server_name, file_map.location, file_map.filename)
    field_list = []
    current_field = lock.field_id
    field_list.append(current_field)
    while current_field.parent_id != None :
        current_field = models.Fields.objects.get(id=current_field.parent_id)
        field_list.append(current_field)
    if path.endswith('json'):
        result, content, message, current = validateJsonEntriesByField(field_list, path)
    else:
        result, content, message, current = validateXmlEntriesByField(field_list, path)
    status_result = "[File path]: %s" %  path
    if message:
        status_result += "\n[File access and field status]: %s" %  message
    
    suspend = models.SuspendActivity.objects.get(environment_id=lock.environment_id)
    if models.FieldsStatus.objects.filter(environment_id=lock.environment_id ,field_id=lock.field_id).exists():
        env_status_str = ""
        for filed_env_status in models.FieldsStatus.objects.filter(environment_id=lock.environment_id ,field_id=lock.field_id):
            if not filed_env_status.enabled:
                env_status_str += "\n Env %s is not enabled.(%s)" % (str(lock.environment_id),Django_Util.getModelUrl(filed_env_status, request))
        if env_status_str != "":
            status_result += "\n[Field Env status]: %s" %  env_status_str
        server_status_str = ""
        for server in models.Servers.objects.filter(environment_id=lock.environment_id, server_type=lock.server_id.server_type):
            if not server.enabled:
                server_status_str += "\n Server %s is not enabled.(%s)" % (str(server.server_name),Django_Util.getModelUrl(server, request))
                
        if server_status_str != "":
            status_result += "\n[Field server status]: %s" %  server_status_str
    if suspend.suspend:
        status_result += "\n[Environment info]: %s is suspended.(%s)" % (lock.environment_id.environment,Django_Util.getModelUrl(suspend, request))
    active_list = models.CurrentLocks.objects.filter(is_active=True, field_id=lock.field_id).exclude(id=lock.id).order_by('-requesttime')
    if len(active_list) != 0:
        status_result +="\n[Conflict locks in active list]: "
        index = 0
        for active_lock in active_list:
            status_result += str(active_lock.id) + ("," if index<(len(active_list)-1) else "" )
            index += 1
    if content:
        status_result += "\n[File Content]:\n%s" % content
    return status_result

def checkLockStatus_b(lock_id):
    lock = models.CurrentLocks.objects.get(id=lock_id)
    server_name = lock.server_id.server_name
    file_map = lock.field_id.file_id
    path = '\\\\%s\\%s\\%s' % (server_name, file_map.location, file_map.filename)
    field_list = []
    current_field = lock.field_id
    field_list.append(current_field)
    while current_field.parent_id != None :
        current_field = models.Fields.objects.get(id=current_field.parent_id)
        field_list.append(current_field)
    if path.endswith('json'):
        result, content, message = validateJsonEntriesByField(field_list, path)
    else:
        result, content, message = validateXmlEntriesByField(field_list, path)
    status_result = "File path: %s" %  path
    status_result += "<br/><b>File access and field status:</b> %s" %  message
    
    suspend = models.SuspendActivity.objects.get(environment_id=lock.environment_id)
    if suspend.suspend:
        status_result += "<br/><b>Environment %s is suspended</b>" % lock.environment_id.environment
    active_list = models.CurrentLocks.objects.filter(is_active=True, field_id=lock.field_id).exclude(id=lock.id).order_by('-requesttime')
    if len(active_list) != 0:
        status_result +="<br/><b>Conflict locks in active list:</b>"
        for active_lock in active_list:
            status_result += str(active_lock.id) + ","
    if content:
        status_result += "<br/><b>File Content:</b><br/>%s" % content
    return status_result

def ajax(request):
    json_posts = ''
    if request.is_ajax():
        context_dict = {}  
        if ACTION_ID in request.GET: 
            action_id = request.GET.get(ACTION_ID)
            if action_id == SUSPEND:
                context_dict[ENVIRONMENT_LIST] = getEnvStatusList(False)
            elif action_id == UNSUSPEND:
                context_dict[ENVIRONMENT_LIST] = getEnvStatusList(True)  
            elif action_id == GET_VALUE_TYPE:
                value_id = request.GET.get(VALUE_ID)
                value_type = models.FieldValues.objects.get(id=value_id).value_type
                if value_type:
                    context_dict[VALUE_TYPE_ID] = str(value_type.id)
                else:
                    context_dict[VALUE_TYPE_ID] = 'NoneSelected' 
            elif action_id == CHECK:
                    if "lock_id" not in request.GET:
                        context_dict['result'] = "lock id is not provided"
                    else:                        
                        lock_id = request.GET.get("lock_id") 
                        context_dict['result'] = checkLockStatus(lock_id, request)
            return HttpResponse(json.dumps(context_dict), content_type=APP_JSON)
            
        elif ACTION_ID in request.POST:    
            action_id = request.POST.get(ACTION_ID)
            if action_id in (ADD_VALUE,CHANGE_VALUE):
                if not can_add_entry(request.user):
                    context_dict[ERROR] = "You don't have the permission to add/change value"
                    return HttpResponse(json.dumps(context_dict), content_type=APP_JSON, status=403)
                post_id = request.POST.get(ID)
                value = request.POST.get(VALUE)
                value_type_id = request.POST.get(VALUE_TYPE_ID) 
                if not value_type_id.isdigit():
                    value_type_id = None
                try: 
                    if action_id == ADD_VALUE:
                        addFieldValue(post_id, value, value_type_id)
                        FileUtil.appendtoFile('%s\configModifier_change_value.log' % (settings.LOG_ROOT_PATH), 
                                              '%s added below value:\n Field id: %s\n Value: %s' %(str(request.user),str(post_id),str(value)))
                    elif action_id == CHANGE_VALUE:
                        old_value = changeFieldValue(post_id, value, value_type_id)
                        FileUtil.appendtoFile('%s\configModifier_change_value.log' % (settings.LOG_ROOT_PATH), 
                                              '%s changed below value:\n Field value id: %s\n Old value: %s\n New value: %s' %(str(request.user),str(post_id),str(old_value),str(value)))
                except Exception as error:
                    context_dict[ERROR] = str(error)
                    return HttpResponse(json.dumps(context_dict), content_type=APP_JSON, status=400)
            return HttpResponse(json.dumps(context_dict), content_type=APP_JSON)
        if (FEATURE_ID in request.GET or CONFIG_ID in request.GET) and HAS_SAME_SERVER_TYPE not in request.GET: 
            if FEATURE_ID in request.GET and request.GET.get(FEATURE_ID).isdigit():  
                feature_id = request.GET.get(FEATURE_ID)
                if models.Features.objects.filter(id=feature_id).exists():
                    config_id = models.Features.objects.get(id=feature_id).field_id.id
            
            elif CONFIG_ID in request.GET and request.GET.get(CONFIG_ID).isdigit():
                config_id = request.GET.get(CONFIG_ID)
            if not config_id:
                return HttpResponse(json.dumps(context_dict), content_type=APP_JSON)  
            file_type = FileTypes.XML
            show_value_type = False
            if models.Fields.objects.filter(id=config_id).exists():
                file_type = str(models.Fields.objects.get(id=config_id).file_id.file_type)
            if file_type == FileTypes.JSON:
                show_value_type = True
            context_dict[SHOW_VALUE_TYPE] = show_value_type
             
            values = models.FieldValues.objects.filter(field_id__id=config_id).order_by(models.FieldValues.FIELD_VALUE)
            value_list = []
            for value in values:
                value_list.append(model_to_dict(value,fields=[ID,models.FieldValues.FIELD_VALUE]))
            if value_list:
                context_dict[VALUE_LIST] = value_list
            return HttpResponse(json.dumps(context_dict), content_type=APP_JSON)
        if TEAM_ID in request.GET and request.GET.get(TEAM_ID).isdigit():                
            features = models.Features.objects.filter(team_id__id=request.GET.get(TEAM_ID)).order_by(models.Features.NAME)
            if ENV_ID in request.GET and request.GET.get(ENV_ID).isdigit():
                environment_id = int(request.GET.get(ENV_ID))
            else:
                return HttpResponse(json.dumps(context_dict), content_type=APP_JSON)
            feature_list = []
            for feature in features:
                if (not feature.ignore_server) and (feature.server_id and feature.server_id.environment_id and feature.server_id.environment_id.id!=environment_id):
                    continue 
                feature_list.append(model_to_dict(feature,fields=[ID,models.Features.NAME]))
            context_dict[FEATURE_LIST] = feature_list
            return HttpResponse(json.dumps(context_dict), content_type=APP_JSON)
       
        if ENV_ID in request.GET or STP_ID in request.GET:
            servers = None
            if ENV_ID in request.GET and request.GET.get(ENV_ID).isdigit():
                environment_id = request.GET.get(ENV_ID)
                servers = models.Servers.objects.filter(environment_id__id=environment_id).order_by(models.Servers.SERVER_NAME)
                                  
            if servers is None:
                servers =  models.Servers.objects.all().order_by(models.Servers.SERVER_NAME)  
                 
            if STP_ID in request.GET and request.GET.get(STP_ID).isdigit():
                server_type_id = request.GET.get(STP_ID)
                servers = servers.filter(server_type__id=server_type_id)
    
            server_list = []
            for server in servers:
                server_list.append(model_to_dict(server,fields=[ID,models.Servers.SERVER_NAME]))
            
            context_dict[SERVER_LIST] = server_list            
        elif SERVER_ID in request.GET and request.GET.get(SERVER_ID).isdigit() and HAS_SAME_SERVER_TYPE in request.GET and  CONFIG_ID in request.GET and  INCLUDE_ALL_SERVERS in request.GET:
            server_id = request.GET.get(SERVER_ID)
            field_id = request.GET.get(CONFIG_ID)
            server_name_str = getServerSameTypeNames(server_id, request.GET.get(INCLUDE_ALL_SERVERS).lower() == 'true')  
            context_dict[SERVER_NAMES] = server_name_str   
            delay, priority_str = getFiledDelay(field_id)
            context_dict[models.Priority.DELAY] = str(delay)
            context_dict[PRIORITY] = priority_str          
        elif SERVER_ID in request.GET and request.GET.get(SERVER_ID).isdigit():
            server_id = request.GET.get(SERVER_ID)   
            serverObj = models.Servers.objects.prefetch_related(models.Servers.SERVER_TYPE).filter(id=server_id).first()
            if serverObj:
                files = models.Filemap.objects.filter(server_type=serverObj.server_type).order_by(models.Filemap.LOCATION, models.Filemap.FILE_NAME)
            file_list = []
            for file in files:
                location = getFileLocation(file)
                file_list.append({ID:file.id, models.Filemap.LOCATION: location})
            context_dict[FILE_LIST] = file_list 
        elif FILE_ID in request.GET and request.GET.get(FILE_ID).isdigit():
            file_id = request.GET.get(FILE_ID)   
            fields = models.Fields.objects.filter(file_id=file_id, to_display=True)
            field_list = []
            for field in fields:
                field_list.append({ID:field.id, models.Fields.DISPLAY: getFieldDisplay(field)})
                
            context_dict[CONFIG_LIST] = field_list  
               
              
        json_posts = json.dumps(context_dict)

    
    return HttpResponse(json_posts, content_type=APP_JSON)

def addFieldValue(fieldId, fieldValue, value_type_id):
    if models.Fields.objects.filter(id=fieldId).exists():
        checkIfFiledValueExisted(fieldId, fieldValue)
        if value_type_id:
            models.FieldValues.objects.create(field_id=models.Fields.objects.get(id=fieldId),field_value=fieldValue,value_type_id=value_type_id);
        else:
            models.FieldValues.objects.create(field_id=models.Fields.objects.get(id=fieldId),field_value=fieldValue);

def changeFieldValue(fieldValueId, fieldValue, value_type_id):
    old_value = ""
    if models.FieldValues.objects.filter(id=fieldValueId).exists():
        fieldValuesObj = models.FieldValues.objects.get(id=fieldValueId)       
        checkIfFiledValueExisted(fieldValuesObj.field_id.id, fieldValue)
        old_value = fieldValuesObj.field_value
        fieldValuesObj.field_value = fieldValue
        if value_type_id:
            fieldValuesObj.value_type_id = value_type_id
        fieldValuesObj.save()
    return old_value
 
def checkIfFiledValueExisted(fieldId, fieldValue): 
    field_oj = models.Fields.objects.get(id=fieldId)
    if len(fieldValue) <= 255:
        if models.FieldValues.objects.filter(field_id=field_oj,field_value=fieldValue).exists():
            raise Exception('Field value already exists!')
    else:
        filedValueSet = models.FieldValues.objects.filter(field_id=field_oj)
        fieldValue = formatLineBreaker(fieldValue)
        if filedValueSet.exists():
            for fvalue in filedValueSet:
                if formatLineBreaker(fvalue.field_value) == fieldValue:
                    raise Exception('Field value already exists!')

def formatLineBreaker(inputStr): 
        return inputStr.replace("\n","\r\n") if not "\r\n" in inputStr else inputStr
    
def team(request, pk,template="team.html"):
    if 'addFeature' in request.POST:       
        addFeatureForm = forms.MakeRequestForm(request.POST)
        if addFeatureForm.is_valid():
            feature_name = addFeatureForm.cleaned_data[forms.MakeRequestForm.FEATURE_NAME]
            field_id = int(addFeatureForm.cleaned_data[forms.MakeRequestForm.CONFIG])
            server_id = int(addFeatureForm.cleaned_data[forms.MakeRequestForm.SERVER])
            ignore_server= addFeatureForm.cleaned_data[forms.MakeRequestForm.IGNORE_SERVER]      
            try:
                if models.Features.objects.filter(team_id__id=pk, name=feature_name).exists():
                    messages.add_message(request, messages.WARNING, ("Feature Name: %s already exists" % feature_name))
                else:
                    feature = models.Features(team_id=models.Team.objects.get(id=pk), field_id=models.Fields.objects.get(id=field_id), 
                                              server_id=models.Servers.objects.get(id=server_id), name=feature_name, ignore_server=ignore_server)  
                    feature.save()                 
            except Exception as e:
                messages.add_message(request, messages.ERROR, "Exception was caught when creating feature: " + str(e))
                return render(request, template)  
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return render(request, template, {'form': addFeatureForm})  
    context = {}
    if not pk:
        return render(request, template, context)  
    
    team = models.Team.objects.get(id=pk)
    team_default = django_apps.get_model('healthcheck.Team').objects.filter(name=team.name).first()
  
    team_name = ''
    if team:
        team_name = team.name
        features = models.Features.objects.prefetch_related(models.Features.FIELD_ID).filter(team_id_id=team.id)
        featureList = []
        for feature in features:
            name = feature.name
            field = feature.field_id
            server = feature.server_id
            server_name = (server.server_name if server else '')
            display = ''
            location = ''
            if field:
                display = getFieldDisplay(field)
                if field.file_id:
                    file = field.file_id
                    location = (file.location if file.location else '') + ('\\' + file.filename if file.filename else '')
                    if file.server_type:
                        server = models.Servers.objects.filter(server_type=file.server_type).first()
                        if feature.ignore_server:
                            server_name = ('%s(%s)' %((server.server_name if server else '' ), str(file.server_type)))
            can_edit_feature = request.user.has_perm(default_models.Team.CHANGE_FEATURE, team_default) 
            can_delete_feature = request.user.has_perm(default_models.Team.DELETE_FEATURE, team_default)
            featureList.append({'name':str(name),'server_name':server_name, 'display':display, 'location':location, 'id':feature.id, 
                                'ignore_server':feature.ignore_server,'can_edit_feature':can_edit_feature,'can_delete_feature':can_delete_feature})
    context['can_add_feature'] = request.user.has_perm(default_models.Team.ADD_FEATURE, team_default)
    context['featureList'] = featureList
    context['team_name'] = str(team_name) + ' Team'  
    form = forms.MakeRequestForm(environment_choices=forms.Choices(choices=getEnvTuple()),st_choices=forms.Choices(choices=getServerTypeTuple()),ftype=forms.MRTFormType.ADDFEATURE);
    context[K_FORM] = form
    context[K_HELP_LINK] = HOME_HELP_URL + "#ConfigModifierTool-Portal-Team"
    return render(request, template, context)   

def feature(request, pk, action, template="feature.html"):
    context = {}  
    if request.method == 'GET':
        if action == EDIT:
            st_choices = None
            feature = models.Features.objects.prefetch_related(models.Features.SERVER_ID,models.Features.FIELD_ID).get(id=int(pk))
            ignore_server_intial = feature.ignore_server
            if feature.server_id is not None:
                server_choices = forms.Choices(choices=((str(feature.server_id.id),str(feature.server_id.server_name)),),initial=str(feature.server_id.id)) 
            else:
                server_choices = None
            if feature.field_id is not None:
                config_choices = forms.Choices(choices=((str(feature.field_id.id),getFieldDisplay(feature.field_id)),),
                                               initial=str(feature.field_id.id))  
                if feature.field_id.file_id is not None:
                    file=feature.field_id.file_id
                    file_choices = forms.Choices(choices=((str(file.id),getFileLocation(file)),),
                                               initial=str(file.id)) 
                    server_type = feature.field_id.file_id.server_type 
                    
                    if server_type is not None:                 
                        st_choices = forms.Choices(choices=getServerTypeTuple(),initial=str(server_type.id))  
                        server = None
                        if not server_choices: 
                            server = models.Servers.objects.filter(server_type=server_type).first()
                        if server:
                            server_choices = forms.Choices(choices=((str(server.id),str(server.server_name)),),initial=str(server.id))                
                else:
                    file_choices = None
            else:
                config_choices = None   


            feature_name = feature.name
            environment_choices = forms.Choices(choices=getEnvTuple())
            if not st_choices:
                st_choices = forms.Choices(choices=getServerTypeTuple())
            
            form = forms.MakeRequestForm(environment_choices=environment_choices,st_choices=st_choices,ftype=forms.MRTFormType.ADDFEATURE
                                         ,server_choices=server_choices, file_choices=file_choices, config_choices=config_choices, feature_name=feature_name
                                         ,ignore_server=ignore_server_intial);
            context[K_FORM] = form
            context[models.Features.TEAM_ID] = str(feature.team_id.id)
            
            return render(request, template, context)  
        if action == DEL:
            try:
                feature = models.Features.objects.get(id=pk)
                context[models.Features.TEAM_ID] = str(feature.team_id.id)
                feature.delete()
            except Exception as e:
                messages.add_message(request, messages.ERROR, "Exception was caught when deleting feature: " + str(e))                 
                return render(request, template,context)  
            else:
                return HttpResponseRedirect(reverse(CONFIGMODIFIER_TEAM, kwargs={'pk': feature.team_id.id}))
    if request.method == 'POST':  
       
        if action == EDIT:
            addFeatureForm = forms.MakeRequestForm(request.POST)
            if addFeatureForm.is_valid():
                feature_name = addFeatureForm.cleaned_data[forms.MakeRequestForm.FEATURE_NAME]
                field_id = int(addFeatureForm.cleaned_data[forms.MakeRequestForm.CONFIG])
                server_id = int(addFeatureForm.cleaned_data[forms.MakeRequestForm.SERVER])     
                ignore_server= addFeatureForm.cleaned_data[forms.MakeRequestForm.IGNORE_SERVER]                 
                try:
                    feature = models.Features.objects.get(id=pk)
                    context[models.Features.TEAM_ID] = str(feature.team_id.id)
                    feature.server_id_id = server_id
                    feature.field_id_id = field_id
                    feature.name = feature_name
                    feature.ignore_server = ignore_server
                    feature.save()            
                except Exception as e:
                    messages.add_message(request, messages.ERROR, "Exception was caught when updating feature: " + str(e))                 
                    return render(request, template,context)  
                else:
                    return HttpResponseRedirect(reverse(CONFIGMODIFIER_TEAM, kwargs={'pk': feature.team_id.id}))
            else:
                return render(request, template, {K_FORM: addFeatureForm})  
       
    return render(request, template, context)   
def getFileLocation(file):
    return str(file.location) + '\\' + str(file.filename)
def getFieldDisplay(field):
    if field:
        return (field.display if field.display else '') + (' ' + field.attribute + '=' if field.attribute else '')
    else:
        return ''
def getCMActionTuple():
    return (
        ('1', 'Suspend'),
        ('2', 'Unsuspend')
    )
def getValueTypeTuple():    
    obj_list = []    
    all_objs = models.ValueTypes.objects.all()  

    for obj in all_objs:
        if not str(obj.value_type) == 'STR':
            obj_list.append((str(obj.id), str(obj.value_type)))   
    return tuple(obj_list)
def getEnvTuple():    
    env_list = []    
    all_envs = models.Environments.objects.all()  

    for env in all_envs:
        if env.enabled == True:
            env_list.append((str(env.id), str(env.environment)))   
    return tuple(env_list)
def getServerTypeTuple():   
    ob_list = []
    for ob in models.ServerTypes.objects.all():
        ob_list.append((str(ob.id), str(ob)))
    ob_list.sort(key=lambda tup: tup[1])
    return tuple(ob_list)
def getTeamTuple():    
    ob_list = []
    for ob in models.Team.objects.all():
        ob_list.append((str(ob.id), str(ob.name)))   
    return tuple(ob_list)
def getCurrentLocksFieldList(Locks, request):       
    result_list = []
    for lock in Locks:
        lock_map = model_to_dict(lock)
        if lock_map["value"] != None and lock_map["value"].isspace():
            lock_map["value"] = "\"%s\"" % lock_map["value"]
        if models.CurrentLocks.REQUESTTIME in lock_map and lock_map[models.CurrentLocks.REQUESTTIME]:
            lock_map[models.CurrentLocks.REQUESTTIME] = lock_map[models.CurrentLocks.REQUESTTIME].strftime('%Y-%m-%d %H:%M:%S')
        if models.CurrentLocks.STARTDATE in lock_map and lock_map[models.CurrentLocks.STARTDATE]:
            lock_map[models.CurrentLocks.STARTDATE] = lock_map[models.CurrentLocks.STARTDATE].strftime('%Y-%m-%d %H:%M:%S')
        filemap_object = lock.field_id.file_id
        file = (r"%s\%s" %(filemap_object.location, filemap_object.filename))
        server = lock.server_id.server_name
        element = (r"<%s %s= >" %(lock.field_id.display, str(lock.field_id.attribute)))   
        user_name = lock.user_id.login
        if (lock.is_active==True or (lock.is_active==False and lock.is_complete==False and lock.is_cancelled==False)):
            lock_map['can_cancel'] = can_cancel_lock(user_name, request)
        if lock.is_active==False and lock.is_complete==False and lock.is_cancelled==False:
            lock_map['can_check'] = can_check_lock(user_name, request)       
        lock_map['file'] = file
        lock_map['server'] = server
        lock_map['element'] = element
        lock_map['user_name'] = user_name
        delay, priority_str = getFiledDelay(field_obj=lock.field_id)
        lock_map[models.Priority.DELAY] = str(delay)
        lock_map[PRIORITY] = priority_str        
        result_list.append(lock_map)
          
    return result_list
def can_cancel_lock(user_name, request, user_ldap_groups=None):
    try:
        user_name_login = (request.user.username if request.user else '')
        if user_name_login ==  user_name or request.user.is_superuser:
            return True
        Team =  django_apps.get_model('healthcheck.Team')
        allTeams = Team.objects.all();
        user =(get_user_model().objects.get(username=user_name) if get_user_model().objects.filter(username=user_name).exists() else None)
        group_match = False
        for team in allTeams:
            if user_ldap_groups:
                for ldap_group in team.ldap_groups.all():
                    if ldap_group.name in user_ldap_groups:
                        group_match = True
                        break
            if (group_match or user in team.users.all()) and request.user.has_perm(default_models.Team.CANCEL_CONFIG, team):
                return True
    except Exception as e:
        messages.add_message(request, messages.ERROR, "Exception was caught when get can_cancel_lock exception: %s" %(str(e)))
        return False    
def can_check_lock(user_name, request, user_ldap_groups=None):
        if request.user.is_superuser:
            return True
        else:
            return False
def getEnvStatusList(suspend=None):
    result_list = []
    for obj in models.SuspendActivity.objects.all():
        obj_map = {}
        if(type(suspend) == bool):
            if obj.suspend != suspend:
                continue
        obj_map['env_id'] = (obj.environment_id.id if obj.environment_id else 0)
        obj_map['env_name'] = (obj.environment_id.environment if obj.environment_id else '')
        is_suspend = (obj.suspend if obj.suspend is not None else False)
        suspender = (obj.suspender.login if obj.suspender else '')
        obj_map['suspend'] = is_suspend
        if is_suspend:
            obj_map['title'] = 'Config Modifier Service is Suspended by %s on this environment' %(suspender)
        else:
            obj_map['title'] = 'Config Modifier Service is Running on this environment'
        
        result_list.append(obj_map)
    return result_list
def can_add_entry(user):
    return user.has_perm('ConfigModifier.add_entry')
def can_change_supend(user):
    return user.has_perm('ConfigModifier.manipulate_suspendactivity')
@user_passes_test(can_add_entry)
def entrySelect(request):
    template = "entry_select.html"
    form = forms.EntrySelectForm(request=request);
    help_url = HOME_HELP_URL + "#ConfigModifierTool-Portal-CreateEntry"
    return render(request, template, {K_FORM: form, K_HELP_LINK: help_url})  
@user_passes_test(can_add_entry)
def entryAdd(request):
    template="entry_add.html"
    ConfigFormSet = formset_factory(forms.EntryForm, min_num=1, extra = 0)
    formset = None
    commonForm = None 
    context = {}
    context[models.Fields.CHANGE_NEED_VALIDATE] = request.user.has_perm('ConfigModifier.change_need_validate')
    context[K_HELP_LINK] = HOME_HELP_URL + "#ConfigModifierTool-Portal-CreateEntry"
    
    if request.method == 'POST': 
        enableParent = False  
        nodeType = ''  
        if forms.EntrySelectForm.NODE_TYPE in request.POST:
            selectForm = forms.EntrySelectForm(request.POST)
            if selectForm.is_valid():
                nodeType= selectForm.cleaned_data[forms.EntrySelectForm.NODE_TYPE]
            formset = ConfigFormSet(form_kwargs={forms.EntrySelectForm.NODE_TYPE: nodeType})
            commonForm = forms.EntryCommonForm()
        elif K_NODE_TYPE_ADD in request.POST:
            commonForm = forms.EntryCommonForm(request.POST)
            nodeType = request.POST.get(K_NODE_TYPE_ADD)
            valueCount = sum( 1 for k in request.POST.keys() if k.startswith("form-0-field_value") )
            formset = ConfigFormSet(request.POST, request.FILES, form_kwargs={forms.EntrySelectForm.NODE_TYPE: nodeType, forms.EntryForm.VALUE_COUNT: valueCount})
        else: 
            commonForm = forms.EntryCommonForm(request.POST)
            formset = ConfigFormSet(request.POST, request.FILES)
        
        enableParent = (True if nodeType == '4' else False)
        
        context[K_FORMSET] = formset
        context[K_COMMON_FORM] = commonForm
        context[K_ENABLE_PARENT] = enableParent
        context[K_NODE_TYPE_ADD] = nodeType
        need_validate = True
        if commonForm.is_valid():
            need_validate = commonForm.cleaned_data[forms.EntryCommonForm.NEED_VALIDATE]
        else: 
            return render(request, template, context)
        if formset.is_valid():
            if need_validate and not validateEntries(formset, commonForm, request):
                return render(request, template, context)   
            else:
                if SUBMIT_TYPE in request.POST:
                    preview = (True if request.POST[SUBMIT_TYPE] == PREVIEW else False)
                else:
                    preview = True
                resultMap = createEntries(formset,commonForm, request, preview)
                preview_xml_str = getPreview(commonForm, formset)
                if request.user.has_perm('ConfigModifier.view_db_entry_preview'):
                    request.session[K_ENTRY_RESULT_MAP] = resultMap
                else:
                    request.session[K_ENTRY_RESULT_MAP] = None
                if preview:
                    context[K_RESULT_LIST] = (resultMap.get(K_RESULT_LIST, None) if request.user.has_perm('ConfigModifier.view_db_entry_preview') else None)
                    context[BLOCK_SUBMIT] = resultMap[BLOCK_SUBMIT]
                    context[PREVIEW] = YES
                    context[K_FORMSET] = formset
                    context[K_COMMON_FORM] = commonForm
#                     context[K_ENABLE_PARENT] = enableParent
                    context[K_NODE_TYPE_ADD] = nodeType
                    context[PREVIEW_XML] = preview_xml_str
                    return render(request, template, context)
                else:
                    return redirect(reverse(CONFIGMODIFIER_ENTRYRESULT)) 
        else:
            return render(request, template, context)   
    else:
        context[K_FORMSET] = None
        context[K_COMMON_FORM] = None
        messages.add_message(request, messages.ERROR, 'Operation not allowed.' )
        return render(request, "entry.html", context)
#         context[K_FORMSET] = ConfigFormSet()
#         context[K_COMMON_FORM] = forms.EntryCommonForm()
    return render(request, template, context)
    
@user_passes_test(can_add_entry)    
def entryResult(request):
    template = "entry_result.html"
    entryResultMap = request.session.get(K_ENTRY_RESULT_MAP, None)
    if K_ENTRY_RESULT_MAP in request.session:
        request.session[K_ENTRY_RESULT_MAP] = None
    resultList = None
    isPreview = None
    if type(entryResultMap) is dict:
        resultList =  entryResultMap.get(K_RESULT_LIST, None)
        isPreview =  entryResultMap.get(K_IS_PREVIEW, None)          
    return render(request, template, {K_RESULT_LIST: resultList, K_IS_PREVIEW:isPreview, K_HELP_LINK: HOME_HELP_URL + "#ConfigModifierTool-Portal-CreateEntry"})   
def getPreview(commonForm,formset):
    networkpath = commonForm.cleaned_data[forms.EntryCommonForm.SHARE_PATH]
    if networkpath.endswith('json'):
        return getJsonPreview(formset,)
    else:
        return getXmlPreview(formset)
def getXmlPreview(formset):
    logger = logging.getLogger("configModifier")
    root = None
    current = None
    try:
        for i, form in reversed(list(enumerate(formset))):
                cleaned_data = form.cleaned_data
                remove_field = cleaned_data[forms.EntryForm.REMOVE_FIELD] 
                remove_attribute = cleaned_data[forms.EntryForm.REMOVE_ATTRIBUTE]      
                element_path = cleaned_data[forms.EntryForm.ELEMENT_PATH].strip()
                attribute = cleaned_data[forms.EntryForm.ATTRIBUTE].strip() 
                field_params =  cleaned_data[forms.EntryForm.FIELD_PARAMS].strip()
                namespace = cleaned_data[forms.EntryForm.NAMESPACE].strip() 
                        
                FieldParaMap = forms.getFieldParaMap(field_params)
                FieldValueList = getFieldValueListFromMap(cleaned_data)
                if FieldValueList:
                    field_value = FieldValueList[0]
                else:
                    field_value = ''
                    
                if attribute and attribute != INNER_TEXT and attribute != INNER_XML:
                    FieldParaMap[attribute] = field_value
                    
                if element_path:
                    element_path = re.sub(r'\[.*\]', '', element_path)
                    if root is None:
                        root = Element(element_path,FieldParaMap)
                        current = root
                    else:
                        current = SubElement(current, element_path, FieldParaMap)
                        
                    if current is not None and attribute == INNER_TEXT:
                        current.text = field_value
                    if current is not None and attribute == INNER_XML and field_value != "":  
                        current.append(ET.XML(str(field_value)))
                        
    except Exception as e:        
        logger.error("Exception was caught when getXmlPreview exception " + str(e))
    
    if root is None:
        return ""
    else:
        return prettify(root)
def getJsonPreview(formset):
    logger = logging.getLogger("configModifier")
    root = None
    current = None
    currentKey = None
    try:
        for i, form in list(enumerate(formset)):
            root = {}
            has_para = False
            cleaned_data = form.cleaned_data 
            element_path = cleaned_data[forms.EntryForm.ELEMENT_PATH].strip()
            attribute = cleaned_data[forms.EntryForm.ATTRIBUTE].strip() 
            field_params =  cleaned_data[forms.EntryForm.FIELD_PARAMS].strip()
                    
            FieldParaMap, error = getJsonFieldParaMap(field_params)
            FieldValueList = getFieldValueListFromMap(cleaned_data)
            
            if FieldParaMap:
                has_para = True
            if FieldValueList:
                field_value = FieldValueList[0]
            else:
                field_value = ''
                
            if attribute:
                FieldParaMap[attribute] = json.loads(field_value) if field_value else ''
            if current and currentKey:
                FieldParaMap[currentKey] = current[currentKey]
                            
            if element_path:
                element_path = element_path.replace("['","").replace("']","")
                element_path_backup = element_path
                element_path = re.sub(r'\[.*\]', '', element_path)
                if has_para or element_path_backup.endswith("]"):
                    element_list = [];
                    element_list.append(FieldParaMap)
                    root[element_path] = element_list
                else:
                    root[element_path] = FieldParaMap
                if element_path == '.':
                    return json.dumps(root[element_path], sort_keys=False, indent=4)
                current =  root
                currentKey = element_path                        
    except Exception as e:        
        logger.error("Exception was caught when getJsonPreview exception " + str(e))
    
    if root is None:
        return ""
    else:
        return json.dumps(root, sort_keys=False, indent=4) 
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, encoding='utf-8')   
    try:
        reparsed = minidom.parseString(rough_string)
        result =re.sub('<\?xml version.*\?>','',reparsed.toprettyxml(indent="  "))
    except:
        result = rough_string
    return result
def makeRequest(request):
    template = "make_request.html"
    if request.method == 'POST':
        if SUBMIT_TYPE in request.POST:
            submit_type = request.POST.get(SUBMIT_TYPE)
            try:
                user_id = getLegacyUserID(request)
                form_valid = False
                servers_same_type = []
                value_type_id = ''
                if submit_type == 'server':
                    form = forms.MakeRequestForm(request.POST)   
                    field_value_lt = forms.MakeRequestForm.FIELD_VALUE_LT       
                    if form.is_valid():
                        environment_id = int(form.cleaned_data[forms.MakeRequestForm.ENVIRONMENT])
                        field_value = form.cleaned_data[forms.MakeRequestForm.FIELD_VALUE]
                        server_id = int(form.cleaned_data[forms.MakeRequestForm.SERVER])
                        timer =  form.cleaned_data[forms.MakeRequestForm.TIMER]
                        config_id = int(form.cleaned_data[forms.MakeRequestForm.CONFIG])
                        include_all_servers = form.cleaned_data[forms.MakeRequestForm.INCLUDE_ALL_SERVERS]
                        value_type_id = form.cleaned_data[forms.MakeRequestForm.VALUE_TYPE]
                        if not value_type_id.isdigit():
                            value_type_id = None
                        if include_all_servers:
                            servers_same_type = getServerSameType(server_id)
                        form_valid = True
                elif submit_type == 'feature':
                    form = forms.MakeRequestByFeatureForm(request.POST) 
                    field_value_lt = forms.MakeRequestByFeatureForm.FIELD_VALUE_LT 
                    if form.is_valid():
                        environment_id = int(form.cleaned_data[forms.MakeRequestByFeatureForm.ENVIRONMENT])
                        field_value = form.cleaned_data[forms.MakeRequestByFeatureForm.FIELD_VALUE]
                        timer =  form.cleaned_data[forms.MakeRequestByFeatureForm.TIMER]
                        feature_id =  form.cleaned_data[forms.MakeRequestByFeatureForm.FEATURE]
                        config_id = models.Features.objects.get(id=feature_id).field_id.id
                        server_id = getServerID(feature_id,environment_id)
                        form_valid = True
                if field_value == '' and form_valid and field_value_lt in form.cleaned_data and form.cleaned_data[field_value_lt] != '':
                    field_value_id = int(form.cleaned_data[field_value_lt])                       
                    field_value = models.FieldValues.objects.get(id=field_value_id).field_value
                if form_valid:              
                    if len(servers_same_type) != 0:
                        for server in servers_same_type:
                            current_lock = models.CurrentLocks(environment_id_id=environment_id,duration=timer,server_id_id=server.id,requesttime=datetime.now(),
                                            user_id_id=user_id,field_id_id=config_id, value=field_value, value_type_id=value_type_id) 
                            current_lock.save()  
                    else:
                        current_lock = models.CurrentLocks(environment_id_id=environment_id,duration=timer,server_id_id=server_id,requesttime=datetime.now(),
                                                       user_id_id=user_id,field_id_id=config_id, value=field_value, value_type_id=value_type_id) 
                        current_lock.save()
                    return redirect(reverse(CONFIGMODIFIER)) 
                else:
                    messages.add_message(request, messages.ERROR, "There are invalid inputs: %s" %(form.errors))
            except Exception as e:
                messages.add_message(request, messages.ERROR, "Exception was caught when creating request, exception: %s" %(str(e)))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
       
    form = forms.MakeRequestForm(environment_choices=forms.Choices(choices=getEnvTuple()),st_choices=forms.Choices(choices=getServerTypeTuple()),value_type_choices=forms.Choices(choices=getValueTypeTuple())); 
    feature_form = forms.MakeRequestByFeatureForm(environment_choices=forms.Choices(choices=getEnvTuple()),team_choices=forms.Choices(choices=getTeamTuple()));
    
    help_url = HOME_HELP_URL + "#ConfigModifierTool-Portal-MakeRequest"
    return render(request, template, {K_FORM: form, K_FEATURE_FORM:feature_form, K_HELP_LINK:help_url})  

def getServerSameType(server_id):
    if server_id and models.Servers.objects.filter(id=server_id).exists():
        server = models.Servers.objects.prefetch_related(models.Servers.ENVIRONMENT_ID,models.Servers.SERVER_TYPE).get(id=server_id)
        serversSameType =  models.Servers.objects.filter(environment_id=server.environment_id, server_type=server.server_type)
        return serversSameType
    else:
        return []
def getServerSameTypeNames(server_id, include_all_servers=False):
    servers = getServerSameType(server_id)
    if not include_all_servers and server_id.isdigit():
        servers = [server for server in servers if server.id == int(server_id)]
    server_names = ""
    if len(servers) != 0:
        server_names = ",".join([server.server_name for server in servers])
    return server_names

def getServerID(feature_id,env_id):      
    try:
        feature = models.Features.objects.prefetch_related(models.Features.FIELD_ID,models.Features.SERVER_ID).get(id=feature_id)
        if not feature.ignore_server:
            return feature.server_id.id
        else:
            return models.Servers.objects.get(server_type=feature.field_id.file_id.server_type, environment_id_id=env_id).id
    except Exception as e:
        raise Exception('Failed to get server id due to ' + str(e))
    
def getLegacyUserID(request):
    try:
        return models.GdUser.objects.get(login=request.user.username).id
    except:
        raise Exception('Failed to get legacy user name ' + request.user.username)
@user_passes_test(can_change_supend)
def cm(request, template = "cm.html"):
    if request.method == 'POST':
        form = forms.CMForm(request.POST)          
        if form.is_valid():
            try:
                environment_id_list = request.POST.getlist(forms.CMForm.ENVIRONMENT)
                action = form.cleaned_data[forms.CMForm.ACTION]
                is_suspend = (1 if action == SUSPEND else 0)
                user_id = getLegacyUserID(request)
                for env_id in environment_id_list:
                    suspend_activity = models.SuspendActivity.objects.get(environment_id_id = env_id)
                    suspend_activity.suspend = is_suspend
                    suspend_activity.suspender_id = user_id
                    suspend_activity.save()  
            except Exception as e:
                messages.add_message(request, messages.ERROR, "Exception was caught when suspending environment, exception: %s" %(str(e)))
            finally:
                return redirect(reverse(CONFIGMODIFIER_CM)) 
        else:
            messages.add_message(request, messages.ERROR, "There are invalid inputs: %s" %(form.errors))
    
    context = {}       
    form = forms.CMForm(environment_choices=forms.Choices(choices=getEnvTuple()),action_choices=forms.Choices(choices=getCMActionTuple()))
    context[K_FORM] = form
    context[ENV_STATUS_LIST] = getEnvStatusList()
    context[K_HELP_LINK] = HOME_HELP_URL + "#ConfigModifierTool-Portal-RE"
    return render(request, template, context)  

def getValueTypeIdFromObj(input_obj, default=1):
    result_id = default
    if type(input_obj) is str:
        result_id = 1
    elif type(input_obj) is int or type(input_obj) is float:
        result_id = 2
    elif type(input_obj) is bool:
        result_id = 5
    elif type(input_obj) is list:
        result_id = 6
    return result_id
def getValueTypeId(input_str,default=1):
    json_obj = None
    result_id = None
    
    try:
        json_obj = json.loads(input_str)
    except:
        raise Exception("Failed to load [%s] to json" % str(input_str))
    
    result_id = getValueTypeIdFromObj(json_obj,default)
    return result_id, str(json_obj)
     
def getValueTypeAndValue(fieldValue, default=1):
    field_value_type = default
    returnValue = fieldValue
    field_value_type_temp, real_value = getValueTypeId(fieldValue,default)

    if field_value_type_temp:
        returnValue = real_value
        field_value_type = field_value_type_temp
    return field_value_type, returnValue
            
def createEntries(formset,commonForm, request, preview=True):
    logger = logging.getLogger("configModifier")
    resultList = []
    server=''
    local_path=''
    result_map = {}
    result_map[BLOCK_SUBMIT] =  NO
    is_json = False
    try:
        networkpath = commonForm.cleaned_data[forms.EntryCommonForm.SHARE_PATH]
        if networkpath.endswith('json'):
            is_json = True
        server, relativePath, fileName = getDirAndFileNameFromSharePath(networkpath)
        serverType = models.Servers.objects.get(server_name=server).server_type
        fileMapObj = models.Filemap.objects.filter(server_type=serverType, filename__iexact=fileName, location__iexact=relativePath).first()
        if fileMapObj:
            fileMap_add = False;
        else:            
            if is_json:
                fileMapObj= models.Filemap(server_type=serverType, filename=fileName, location=relativePath, file_type_id=2) 
            else:
                fileMapObj= models.Filemap(server_type=serverType, filename=fileName, location=relativePath)    
            if not preview:
                fileMapObj.save()          
            fileMap_add = True;
        fileMapLabel = ('server_type={%s},filename={%s},location={%s},file_type={%s}' %(str(serverType), str(fileName), str(relativePath), str(fileMapObj.file_type)))
        tempResult = EntryAddResult(label=fileMapLabel, id=fileMapObj.id, link=Django_Util.getModelUrl(fileMapObj, request), type=FILE_MAP, new_add=fileMap_add, modelObj=fileMapObj).toJSON()
        resultList.append(tempResult)
        form_parent_id = None
        for i, form in reversed(list(enumerate(formset))):
            cleaned_data = form.cleaned_data
            remove_field = cleaned_data[forms.EntryForm.REMOVE_FIELD] 
            remove_attribute = cleaned_data[forms.EntryForm.REMOVE_ATTRIBUTE]      
            element_path = cleaned_data[forms.EntryForm.ELEMENT_PATH].strip()
            attribute = cleaned_data[forms.EntryForm.ATTRIBUTE].strip() 
            field_params =  cleaned_data[forms.EntryForm.FIELD_PARAMS].strip()
            namespace = cleaned_data[forms.EntryForm.NAMESPACE].strip() 
            if not form_parent_id:
                parent_id = cleaned_data[forms.EntryForm.PARENT_ID]
            else:
                parent_id = form_parent_id
            
            if is_json:
                FieldParaMap, error = getJsonFieldParaMap(field_params)
            else:               
                FieldParaMap = forms.getFieldParaMap(field_params)
            FieldValueList = getFieldValueListFromMap(cleaned_data)
            
            namespace = None if namespace == '' else  namespace
            if namespace:
                fieldObjList = models.Fields.objects.filter(file_id=fileMapObj,element_path=element_path, attribute=attribute, parent_id=parent_id
                                     ,namespace=namespace,remove_field=remove_field,remove_attribute=remove_attribute)
            else:
                fieldObjList = models.Fields.objects.filter(Q(namespace__isnull=True) | Q(namespace__exact=''), file_id=fileMapObj,element_path=element_path, attribute=attribute, parent_id=parent_id
                                     ,remove_field=remove_field,remove_attribute=remove_attribute)
                                        
            fieldObj = fieldObjList.first() if fieldObjList else None
            messages_add = False
            if fieldObj:            
                field_exist = True
                if len(FieldParaMap) != 0:
                    for innerfieldObj in fieldObjList:
                        matchCount = 0
                        for paraKey in FieldParaMap:                        
                            fieldParamsObj = models.FieldParams.objects.filter(field_id=innerfieldObj,param=paraKey,value=FieldParaMap[paraKey]).first()                        
                            if not fieldParamsObj:
                                field_exist = False
                            else:
                                matchCount += 1
                        if len(FieldParaMap) == matchCount:
                            field_exist = True
                            fieldObj = innerfieldObj
                            if i == 0:
                                messages.add_message(request, messages.ERROR, "The entry you are adding [Search parameters: %s ] already exists, duplicated entry will not be inserted" %(str(FieldParaMap)))
                                result_map[BLOCK_SUBMIT] =  YES
                                messages_add = True
                            break
                        else:
                            field_exist = False 
                               
                elif models.FieldParams.objects.filter(field_id=fieldObj).exists():
                    field_exist = False
                if field_exist and len(FieldValueList) != 0 :
                    for fieldValue in FieldValueList:
                        fieldValueObj = models.FieldValues.objects.filter(field_id=fieldObj,field_value=fieldValue).first() 
                        if fieldValueObj:
                            fieldValue_add = False
                        else:                           
                            if is_json:
                                field_value_type, fieldValue = getValueTypeAndValue(fieldValue, None)
                                if not field_value_type:
                                    raise Exception('Unsupport value type of "%s"' % fieldValue)
                                fieldValueObj = models.FieldValues(field_id=fieldObj,field_value=fieldValue,value_type_id=field_value_type) 
                            else:
                                fieldValueObj = models.FieldValues(field_id=fieldObj,field_value=fieldValue) 
                            if not preview:
                                fieldValueObj.save()
                            fieldValue_add = True
                        fieldValueLabel = ('field_id={%s},field_value={%s},value_type={%s}' %(str(fieldObj.id), str(fieldValue),str(fieldValueObj.value_type)))
                        resultList.append(EntryAddResult(label=fieldValueLabel, id=fieldValueObj.id, link=Django_Util.getModelUrl(fieldValueObj, request), type=FIELD_VALUE, new_add=fieldValue_add).toJSON())
            else:
                field_exist = False
                
            if field_exist and not messages_add:
                if i == 0: # leaf node
                    messages.add_message(request, messages.ERROR, "The entry you are adding [path: %s ] already exists, duplicated entry will not be inserted" %(str(element_path)))
                    result_map[BLOCK_SUBMIT] =  YES
                else:
                    messages.add_message(request, messages.WARNING, "The entry you are adding [path: %s ] already exists, duplicated entry will not be inserted" %(str(element_path)))
               
                messages_add = True
                
            if not field_exist: 
                fieldObj = models.Fields(file_id=fileMapObj,element_path=element_path, attribute=attribute, parent_id=parent_id
                                     ,namespace=namespace,remove_field=remove_field,remove_attribute=remove_attribute,enabled=False)  
                if not preview:  
                    fieldObj.save()
                     
                field_add = True 
            else:
                field_add = False 
            fieldLabel = ('file_id={%s},element_path={%s},attribute={%s},parent_id={%s},namespace={%s},remove_field={%s},remove_attribute={%s}' %(str(fileMapObj.id), str(element_path), str(attribute), 
                                                                                                                                    str(parent_id), str(namespace), str(remove_field), str(remove_attribute)))   
            resultList.append(EntryAddResult(label=fieldLabel, id=fieldObj.id, link=Django_Util.getModelUrl(fieldObj, request), type=FIELD, new_add=field_add).toJSON())
            if not field_exist and preview:
                form_parent_id = -1
            else:
                form_parent_id = fieldObj.id
            if field_add:
                for paraKey in FieldParaMap: 
                    if is_json:
                        fieldParamsObj = models.FieldParams(field_id=fieldObj,param=paraKey,value=str(FieldParaMap[paraKey]),value_type_id=getValueTypeIdFromObj(FieldParaMap[paraKey],1))
                    else:
                        fieldParamsObj = models.FieldParams(field_id=fieldObj,param=paraKey,value=FieldParaMap[paraKey])
                    if not preview:
                        fieldParamsObj.save()   
                    fieldParamsLabel = ('field_id={%s},param={%s},value={%s},value_type={%s}' %(str(fieldObj.id), str(paraKey), str(FieldParaMap[paraKey]),str(fieldParamsObj.value_type))) 
                    resultList.append(EntryAddResult(label=fieldParamsLabel, id=fieldParamsObj.id, link=Django_Util.getModelUrl(fieldParamsObj, request), type=FIELD_PARAM, new_add=True).toJSON())
                
                for fieldValue in FieldValueList: 
    
                    if is_json:
                        field_value_type, fieldValue = getValueTypeAndValue(fieldValue, None)
                        if not field_value_type:
                            raise Exception('Unsupport value type of "%s"' % fieldValue)
                        fieldValueObj = models.FieldValues(field_id=fieldObj,field_value=fieldValue,value_type_id=field_value_type) 
                    else:
                        fieldValueObj = models.FieldValues(field_id=fieldObj,field_value=fieldValue)
                           
                    if not preview:
                        fieldValueObj.save()   
                    fieldValueLabel = ('field_id={%s},field_value={%s},value_type={%s}' %(str(fieldObj.id), str(fieldValue), str(fieldValueObj.value_type)))       
                    resultList.append(EntryAddResult(label=fieldValueLabel, id=fieldValueObj.id, link=Django_Util.getModelUrl(fieldValueObj, request), type=FIELD_VALUE, new_add=True).toJSON())
    except Exception as e:
        logger.error("Exception was caught when creating configmodifier entry, server:%s path:%s \n%s" %(server,local_path,traceback.format_exc())) 
        messages.add_message(request, messages.ERROR, "Exception was caught when creating configmodifier entry, server:%s path:%s exception: %s" %(server,local_path,str(e)))
        result_map[BLOCK_SUBMIT] =  YES
    if len(resultList) != 0 and not preview:    
        FileUtil.appendtoFile('%s\configModifier_add_entry.log' % (settings.LOG_ROOT_PATH), str(request.user) + ' created below entries:\n' + '\n'.join([str(re) for re in resultList]))
    
    result_map["resultList"] = resultList
    result_map["isPreview"] = preview
    
    return result_map

def validateXmlEntries(formset,commonForm, request):
    
    networkpath = commonForm.cleaned_data[forms.EntryCommonForm.SHARE_PATH]
    is_accessible, fileBytes, return_msg = checkNetWorkPathAccessible(networkpath, request)
     
    if not is_accessible:
        messages.add_message(request, messages.ERROR, 'Path: '+ networkpath + ' is not accessible or writable(RE-18432). message: ' + return_msg)
        return is_accessible
    index = ""
    xpath = r'//'
    has_default_namespace = False
    has_index = False
    for i, form in reversed(list(enumerate(formset))):
        has_index = False
        index = ""
        cleaned_data = form.cleaned_data
        remove_field = (cleaned_data[forms.EntryForm.REMOVE_FIELD] if forms.EntryForm.REMOVE_FIELD in cleaned_data else False)
        remove_attribute = (cleaned_data[forms.EntryForm.REMOVE_ATTRIBUTE] if forms.EntryForm.REMOVE_ATTRIBUTE in cleaned_data else False)        
        if remove_field:
            continue;
        element_path = (cleaned_data[forms.EntryForm.ELEMENT_PATH].strip() if forms.EntryForm.ELEMENT_PATH in cleaned_data else '')
        attribute = (cleaned_data[forms.EntryForm.ATTRIBUTE].strip() if forms.EntryForm.ATTRIBUTE in cleaned_data else '')
        field_params =  (cleaned_data[forms.EntryForm.FIELD_PARAMS].strip() if forms.EntryForm.FIELD_PARAMS in cleaned_data else '')
        namespace =  (cleaned_data[forms.EntryForm.NAMESPACE].strip() if forms.EntryForm.NAMESPACE in cleaned_data else '')
        
        index_match = re.search(r"(?P<index>\[(?!-)\d+(?<!-)\]?)", element_path, re.IGNORECASE)
        if index_match:
            index = index_match.group('index')
        if index:
            has_index = True
            element_path = element_path.replace(index, "")
        if has_index :
            xpath = "(" + xpath
               
        if namespace :
            has_default_namespace = True
            element_path = 'test:' + element_path

        if xpath.endswith(r'//'):
            xpath += element_path
        else:
            xpath += r'//' + element_path  
        FieldParaMap = forms.getFieldParaMap(field_params)
        if FieldParaMap:
            xpath += '[' 
        for key in FieldParaMap:
            xpath += (r"@%s='%s' and" % (key, FieldParaMap[key]))
        if xpath.endswith('and'):
            xpath = xpath[:-3]
        if FieldParaMap:
            xpath += ']' 
        if attribute and i == 0 and not remove_attribute and attribute != INNER_TEXT and attribute != INNER_XML:  # first form
            xpath += r'/@' + attribute
        
        if has_index :
            xpath +=  ")" + index
            
        if not attribute and i == 0 and not remove_field and not remove_attribute:
            messages.add_message(request, messages.ERROR, 'Attribute of xml leaf node can not be empty.') 
            return False   
         
    if xpath == r'//':
        return True      
    name_space_map = {"xsl":"http://www.w3.org/1999/XSL/Transform"}
    if has_default_namespace:
        name_space_map["test"] =  namespace
    result, is_found = XmlUtil.get_str_element_result_flag( fileBytes, xpath, name_space_map)    
    if not is_found:
        messages.add_message(request, messages.ERROR, 'Node does not exist xpath: ' + xpath )
        return False
    else:
        return True

def getJsonFieldParaMap(fieldParas:str):    
    para_map = {} 
    error = ''
    if not fieldParas.startswith('{'):
        fieldParas = '{' + fieldParas + '}'   
    try:      
        para_map = json.loads(fieldParas)
    except Exception as e:
        error = 'failed to load string as json: [%s] due to error %s'  %(str(fieldParas), str(e))
    
    return para_map, error
def validJsonMap(FieldParaMap):
    error = ''
    for key in FieldParaMap:
        if type(FieldParaMap[key]) not in (str,int,float):
            return  "Value type of [%s] is not supported, only support str/int/float" % FieldParaMap[key]
    return error
def getPathString(input_var):
    path = ""
    if type(input_var) is str:
        path = "\"%s\"" %(input_var)
    else:
        path = str(input_var)
    return path
def validateJsonEntries(formset,commonForm, request):
    
    networkpath = commonForm.cleaned_data[forms.EntryCommonForm.SHARE_PATH]
    is_accessible, fileBytes, return_msg = checkNetWorkPathAccessible(networkpath, request)
     
    if not is_accessible:
        messages.add_message(request, messages.ERROR, 'Path: '+ networkpath + ' is not accessible or writable(RE-18432). message: ' + return_msg)
        return is_accessible
    index = ""
    has_index = False

    data = fileBytes.decode("utf-8")
    #remove BOM header
    if data.startswith(u'\ufeff'):
        data = data.encode('utf8')[3:].decode('utf8')
        
    for i, form in reversed(list(enumerate(formset))):
        path = r'$..'
        has_index = False
        index = ""
        cleaned_data = form.cleaned_data
        remove_field = (cleaned_data[forms.EntryForm.REMOVE_FIELD] if forms.EntryForm.REMOVE_FIELD in cleaned_data else False)     
        if remove_field:
            continue;
        element_path = (cleaned_data[forms.EntryForm.ELEMENT_PATH].strip() if forms.EntryForm.ELEMENT_PATH in cleaned_data else '')
        field_params =  (cleaned_data[forms.EntryForm.FIELD_PARAMS].strip() if forms.EntryForm.FIELD_PARAMS in cleaned_data else '')
        attribute = (cleaned_data[forms.EntryForm.ATTRIBUTE].strip() if forms.EntryForm.ATTRIBUTE in cleaned_data else '')        
        
        if element_path.startswith("."):
            path =  r'$.'
            element_path = element_path.replace(".","")  
               
        index_match = re.search(r"(?P<index>\[(?!-)\d+(?<!-)\]?)", element_path, re.IGNORECASE)
        if index_match:
            index = index_match.group('index')
        if index:
            has_index = True
            element_path = element_path.replace(index, "")
        if has_index :
            path += element_path + index
        else:
            FieldParaMap, error = getJsonFieldParaMap(field_params)
            if error:
                messages.add_message(request, messages.ERROR, error)
                return False
            errorJsonMap = validJsonMap(FieldParaMap)
            if errorJsonMap:
                messages.add_message(request, messages.ERROR, errorJsonMap)
                return False
            path += element_path
            if FieldParaMap:
                path += '[?(' 
                for key in FieldParaMap:
                    path += (r"@.%s == %s" % (key, getPathString(FieldParaMap[key])))
                    if list(FieldParaMap.keys())[-1] != key:
                        path += " & "
                path += ')]'
#                 objectPath
#             if FieldParaMap:
#                 path += '[' 
#                 for key in FieldParaMap:
#                     path += (r"@.%s is %s" % (key, getPathString(FieldParaMap[key])))
#                     if list(FieldParaMap.keys())[-1] != key:
#                         path += " and "
#                 path += ']'
        if not attribute and i == 0:
            messages.add_message(request, messages.ERROR, 'Attribute of json leaf node can not be empty.') 
            return False
        if attribute and i == 0: # means the leaf node
            path += ('' if path.endswith(".") else '.' )+ attribute
            
        data, is_found, error = JsonUtil.get_str_element_result_flag( data, path)  
        if not is_found:
            messages.add_message(request, messages.ERROR, ('Node does not exist path: %s, error: %s' % (path, error)))
            return False
    
    return True    

def validateEntries(formset,commonForm, request):
    networkpath = commonForm.cleaned_data[forms.EntryCommonForm.SHARE_PATH]
    if networkpath.endswith('json'):
        return validateJsonEntries(formset,commonForm, request)
    else:
        return validateXmlEntries(formset,commonForm, request)
    
def getFieldValueList(fieldValues:str)-> []:
    return_list = []
        
    for fvalue in fieldValues.split('\r\n'):
        if fvalue:
            return_list.append(fvalue.strip())
    
    return return_list
def getFieldValueListFromMap(fieldMap:{})-> []:

    return [v for (k,v) in fieldMap.items() if k.startswith("field_value") and v != None and v.strip() != "" ]

def getDirAndFileNameFromSharePath(path:str):  
    
    pattern = re.compile(r"(?P<server>^\\\\(?!-)[a-z0-9-.]{1,100}(?<!-)\\?)(?P<middle>([^\\]+\\)+)(?P<file>([^\\])+$)",re.IGNORECASE)
    match = pattern.match(path)
    server = ''
    relativePath = ''
    file = ''
    if match:
        server = match.group('server').replace('\\','')
        relativePath = match.group('middle')[:-1].strip()
        file = match.group('file').strip()
    
    return server, relativePath, file


def checkNetWorkPathAccessible(remote_path:str, request=None) -> (bool, bytes, str):
    USER_NAME = r'nextestate\svc_qa_configmgr'
    USER_PASSWORD = r'PrapE5wu'
    return_msg = ''
    is_accessible = False
    fileBytes = None
    file = None
    try:
        with network_share_auth(remote_path, USER_NAME, USER_PASSWORD, request):
            if request is not None and ('127.0.0.1' in request.get_host() or "testserver" in request.get_host()):
                file = open(remote_path, mode='r', encoding='utf-8')
            else:
                file = open(remote_path, mode='r+', encoding='utf-8')
            print(file)
            fileBytes = file.read().encode('utf-8')
            is_accessible = True
    except Exception as e:
            print('Found exception ' + str(e))
            return_msg = str(e)
    finally:
        if file:
            file.close()  
            
        return is_accessible, fileBytes, return_msg
        
def checkFieldAttrbutes(fileBytes:bytes, configEntries:list) -> (bool, int):
    xpath = ''
    XmlUtil.get_str_element( fileBytes, xpath, {}) 
    
@contextmanager
def network_share_auth(share, username=None, password=None, request=None, drive_letter=None):
    """Context manager that mounts the given share using the given
    username and password to the given drive letter when entering
    the context and unmounts it when exiting."""
    if request is not None and ('127.0.0.1' in request.get_host() or "testserver" in request.get_host()):
        need_run = False
    else:
        need_run = True    
        
    if drive_letter:
        cmd_parts = ["NET USE %s: \"%s\"" % (drive_letter, share)]
    else:
        cmd_parts = ["NET USE \"%s\"" % (share)]
    if username and password:
        cmd_parts.append("/USER:%s" % username)
        cmd_parts.append(password)
#     print('mounting ' + " ".join(cmd_parts))
    if need_run:
        os.system(" ".join(cmd_parts))
    try:
        yield
    finally:
        if need_run:
            os.system("NET USE /DELETE \"%s\"" % share)   