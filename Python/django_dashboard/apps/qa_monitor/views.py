from django.shortcuts import render
from apps.qa_monitor.models import Environment, MonitorSchedule , Run, OperationRun, RunResult, Processor, IndividualServer
import json
from django.http.response import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from apps.qa_monitor.dto.result import Result
from collections import OrderedDict 
from common_utils.celery import get_interval_cron
from common_utils.str_util import StrUtil
from common_utils.constant import Constant
from common_utils.django_util import Django_Util
from django.forms.models import model_to_dict
import django
def schedule_monitor(request):
    print("Calling Schedule_monitor")
    context_dict = {}
    processor_dict = {}
    environment_dict = {}
    for processor in Processor.objects.all():
        processor_dict[processor.id] = processor.name
    
    for environment in Environment.objects.all():
        environment_dict[environment.id] = environment.name
        
    context_dict['environment_dict'] = environment_dict
    context_dict['processor_dict'] = processor_dict
    get_interval_cron(context_dict)
    
    if request.is_ajax() and request.method == 'POST':
        
        environment_id = request.POST.get('environment_id')
        server_id = request.POST.get('server_id')
        processor_id = request.POST.get('processor_id')
        operation_id = request.POST.get('operation_id')
        monitor_name = request.POST.get('monitor_name')
        monitor_desc = request.POST.get('monitor_desc')
        interval_id = request.POST.get('interval_id')
        cron_id = request.POST.get('cron_id')
        enabled = (request.POST.get('enabled') == 'TRUE')
        monitor_id = request.POST.get('monitor_id')
        monitor_recipient_list =  request.POST.get('monitor_recipient_list')
        skip_success = (request.POST.get('skip_success') == 'TRUE') 
        store_result = (request.POST.get('store_result') == 'TRUE')
        email_title = request.POST.get('monitor_email_title')
        
        if 'remove' in request.POST:
            try:
                monitor_object = MonitorSchedule.objects.get(id=monitor_id)
            except:
                monitor_object = None
            if monitor_object:
                monitor_object.terminate()
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_Y})
            else:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Monitor doesn't exist"})
            return HttpResponse(json_posts, content_type='application/json')
        
        elif 'create' in request.POST or 'update' in request.POST:
             
            if not monitor_name:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Monitor Name is empty"})
                return HttpResponse(json_posts, content_type='application/json')       
            try:
                environment_obj =  Environment.objects.get(id=environment_id)
            except:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Environment %s does not exist" % (environment_id)})
                return HttpResponse(json_posts, content_type='application/json')
            try:
                if server_id and server_id.isdigit():
                    server_obj =  IndividualServer.objects.get(id=server_id)
                else:
                    server_obj = None
            except:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Server %s does not exist" % (server_id)})
                return HttpResponse(json_posts, content_type='application/json')
            try:
                processor_obj =  Processor.objects.get(id=processor_id)
            except:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Processor %s does not exist" % (processor_id)})
                return HttpResponse(json_posts, content_type='application/json')
            if processor_obj and processor_obj.model:
                operation_model = Django_Util.getModel(Constant.QA_MONITOR_LABEL, processor_obj.model)
                if operation_model:
                    try:
                        operation_obj =  operation_model.objects.get(id=operation_id)
                    except:
                        json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Operation %s does not exist" % (operation_id)})
                        return HttpResponse(json_posts, content_type='application/json')
            if 'update' in request.POST:
                monitor_id = request.POST.get('monitor_id')
                monitor_object = MonitorSchedule.objects.get(id=monitor_id)
                
                if MonitorSchedule.objects.filter(environment=environment_obj, processor=processor_obj, operation_id=operation_id, server=server_obj).exclude(id=monitor_id).exists():                   
                    json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Monitor already exists for %s environment %s processor %s operation" % (processor_obj.name, environment_obj.name, operation_obj.name)})
                    return HttpResponse(json_posts, content_type='application/json')
            elif 'create' in request.POST:
                 
                if MonitorSchedule.objects.filter(environment=environment_obj, processor=processor_obj, operation_id=operation_id, server=server_obj).exists():
                    json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR: "Monitor already exists for %s environment %s processor %s operation" % (processor_obj.name, environment_obj.name, operation_obj.name)})
                    return HttpResponse(json_posts, content_type='application/json')     
                else:
                    monitor_object = MonitorSchedule.objects.create(name=monitor_name, environment=environment_obj, processor=processor_obj, description=monitor_desc)
                    monitor_object.save() 
                    if request.user and User.objects.filter(username=request.user.username).exists():        
                        monitor_object.set_owner(request.user)            
            monitor_object.name = monitor_name
            monitor_object.description = monitor_desc
            monitor_object.environment = environment_obj
            monitor_object.processor = processor_obj
            monitor_object.operation_id = operation_id
            monitor_object.recipient_list = monitor_recipient_list
            monitor_object.skip_success = skip_success
            monitor_object.store_result = store_result
            monitor_object.server = server_obj
            monitor_object.email_title = email_title
            monitor_object.save()
            environment_name = (environment_obj.name if environment_obj else Constant.NA)
            monitor_name_env = ('%s (%s)' %(monitor_name, environment_name))
            data = [{
                  "monitorId" : monitor_object.id,
                  "environmentId" : environment_obj.id,
                  "processorId" : processor_obj.id,
                  "operationId" : operation_id
            }]
            try:
                monitor_object.schedule_edit_every(monitor_name_env, "apps.qa_monitor.tasks.processMonitors", enabled, interval_id, cron_id, json.dumps(data), sameName=False)
            except Exception as e:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_N, Result.ERROR : str(e)})
            else:
                json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_Y, Result.ERROR : ""})              
                    
            return HttpResponse(json_posts, content_type='application/json')
    elif request.is_ajax() and request.method == 'GET' and 'environment_id' in request.GET and 'processor_id' in request.GET:
        processor = Processor.objects.get(id=request.GET.get('processor_id'))
        context_dict = OrderedDict()
        if processor and processor.model:
            context_dict['operation_dict'] = getOperationLinkDict(Constant.QA_MONITOR_LABEL, processor.model, request.GET.get('environment_id'), request)
        else:
            print('Can not find processor with id = %s or processor have no model'% (request.GET.get('processor_id')))
        json_posts = json.dumps(context_dict) 
        return HttpResponse(json_posts, content_type='application/json')
    elif request.is_ajax() and request.method == 'GET' and 'environment_id' in request.GET:
        environment_id = request.GET.get('environment_id')
        servers = IndividualServer.objects.filter(environment__id=environment_id)
        server_dict = {}
        for server in servers:
            server_dict[server.id] = server.name
        context_dict['server_dict'] = server_dict  
        return HttpResponse(json.dumps(context_dict), content_type='application/json')
    elif request.method == 'GET' and 'id' in request.GET:       
        try:
            Monitor_object = MonitorSchedule.objects.get(id=request.GET.get('id'))
        except:
            messages.add_message(request, messages.ERROR, "Monitor schedule doesn't exist")
            return render(request, 'schedule_monitor.html', context_dict)         
        if Monitor_object.get_owner() == None or request.user ==  Monitor_object.get_owner() or request.user.is_superuser :
            context_dict['is_owner'] = 'true'
        else:
            context_dict['is_owner'] = 'false'
        periodic_task = Monitor_object.get_periodic_task()
        processor_id = ''
        if periodic_task: 
            if periodic_task.interval:
                context_dict['interval_id'] = periodic_task.interval.id
            if periodic_task.crontab:
                context_dict['cron_id'] = periodic_task.crontab.id      
            context_dict['enabled'] =   periodic_task.enabled
            periodic_task_args = json.loads(periodic_task.args)[0]
            context_dict['processor_id'] = periodic_task_args.get('processorId')
            processor_id = periodic_task_args.get('processorId')
            context_dict['operation_id'] = periodic_task_args.get('operationId')
        get_interval_cron(context_dict)
        
        environment = ""
        context_dict['monitor_name'] = Monitor_object.name
        context_dict['monitor_id'] = Monitor_object.id
        if Monitor_object.description:
            context_dict['monitor_desc'] = Monitor_object.description
        if Monitor_object.recipient_list:
            context_dict['monitor_recipient_list'] = Monitor_object.recipient_list
        if Monitor_object.environment:
            context_dict['environment_id'] = Monitor_object.environment.id
            if processor_id and Processor.objects.filter(id=processor_id).exists():
                context_dict['operation_dict'] = getOperationLinkDict(Constant.QA_MONITOR_LABEL,  Processor.objects.get(id=processor_id).model, context_dict['environment_id'],request)
        if Monitor_object.get_owner():
            context_dict['monitor_owner'] = Monitor_object.get_owner().username
        if Monitor_object.email_title:
            context_dict['monitor_email_title'] = Monitor_object.email_title
        
        server_dict = {}
        if Monitor_object.server:
            context_dict['server_id'] = Monitor_object.server.id
            server_dict[Monitor_object.server.id] = Monitor_object.server.name
        
        context_dict['server_dict'] = server_dict
        context_dict['skip_success'] = Monitor_object.skip_success
        context_dict['store_result'] = Monitor_object.store_result
        return render(request, 'schedule_monitor.html', context_dict)
    else:       
        return render(request, 'schedule_monitor.html', context_dict)
def getOperationDict(appLabel, modelName, environment_id):
    operation_dict = OrderedDict()
    if environment_id and Environment.objects.filter(id=environment_id).exists():
        environmentObj = Environment.objects.get(id=environment_id)
    else:
        print('Environment id = %s does not exist' % (environment_id))
        return operation_dict

    operation_model = Django_Util.getModel(appLabel, modelName)
    if not operation_model:
        return operation_dict
    for operation in operation_model.objects.all():
        if operation.environment == environmentObj:
            operation_dict[operation.id] = str(operation)
    return  operation_dict
def getOperationLinkDict(appLabel, modelName, environment_id, request):
    operation_dict = OrderedDict()
    if environment_id and Environment.objects.filter(id=environment_id).exists():
        environmentObj = Environment.objects.get(id=environment_id)
    else:
        print('Environment id = %s does not exist' % (environment_id))
        return operation_dict

    operation_model = Django_Util.getModel(appLabel, modelName)
    if not operation_model:
        return operation_dict
    for operation in operation_model.objects.all():
        if operation.environment == environmentObj:
            operation_dict[operation.id] = {'operation':str(operation), 'url':Django_Util.getModelUrl(operation, request)}
    return  operation_dict
def getRequestMsg(appLabel, schedule_id):
    requst_msg = ''
    if appLabel and schedule_id and MonitorSchedule.objects.filter(id=schedule_id).exists():
        schedule_obj = MonitorSchedule.objects.get(id=schedule_id)
        if schedule_obj.processor and schedule_obj.operation_id:
            operation_obj = getOperation(appLabel, schedule_obj.processor.id, schedule_obj.operation_id)
            requst_msg = operation_obj.request_msg()
    
    return requst_msg

def getOperation(appLabel, processor_id, operation_id):
    operation_model = None
    operation_obj = None
    if processor_id and Processor.objects.filter(id=processor_id).exists() :
        model_name = Processor.objects.get(id=processor_id).model
        if model_name and operation_id:
            try:
                operation_model =  django.apps.apps.get_model(appLabel, model_name)
            except LookupError as e:
                print(e)
                return None
            else:
                if operation_id and operation_model.objects.filter(id=operation_id).exists():
                    operation_obj = operation_model.objects.get(id=operation_id)
                else:
                    print('operation_id %s does not exist' % operation_id)
                    return None

    return  operation_obj   
def view_runs(request):

    if request.is_ajax() and "run_id" in request.POST and 'operation' in request.POST:
        run_id = request.POST.get('run_id')
        operation = request.POST.get('operation')
        if run_id:
            run_obj =  Run.objects.get(id=run_id)
            if run_obj:
                if operation == 'remove':
                    run_obj.delete()
        json_posts = json.dumps({Result.SUCCESS : Result.SUCCESS_Y})
        return HttpResponse(json_posts, content_type='application/json')
    else:
        
        context_dict = {}
        schedule_run_map = OrderedDict()
        
        if 'sid' in request.GET:
            ScheduleList = MonitorSchedule.objects.filter(id=request.GET.get('sid'))
        else: 
            ScheduleList = MonitorSchedule.objects.all()
        if ScheduleList:
            for schedule in ScheduleList:
                run_dic = {}
                runs = []
                for run in Run.objects.filter(schedule=schedule).order_by('-startDate'):
                    run_fields = model_to_dict(run, fields=[field.name for field in run._meta.fields])
                    run_fields['status_name'] = run.status.name
                    run_fields['result_name'] = run.result.name
                    runs.append(run_fields)
                run_dic = {'schedule_id': schedule.id, 'runs': runs}
                schedule_run_map[schedule.name_env()] = run_dic
        context_dict['schedule_run_map'] = schedule_run_map
        return render(request, 'monitor_run.html' , context_dict)

def view_monitors(request):
    context_dict = {}
    schedule_maps = OrderedDict()
    for monitor_object in MonitorSchedule.objects.exclude(name__isnull=True):    
        schedule_map = OrderedDict()
        schedule_map['id'] = monitor_object.id          
        if monitor_object.get_owner():
            schedule_map['owner'] = monitor_object.get_owner().username
        else:
            schedule_map['owner'] = "N/A"
        if monitor_object.environment :
            schedule_map['environment'] = monitor_object.environment.name
        else:
            schedule_map['environment'] = "N/A"
        schedule_map['name'] = monitor_object.name_env()
        schedule_map['latest_result'] = (monitor_object.latest_result.name if monitor_object.latest_result else "N/A")
        periodic_task = monitor_object.get_periodic_task()
        if periodic_task:
            schedule_map['enabled'] = str(periodic_task.enabled)
            if not periodic_task.last_run_at:
                schedule_map['last_run_at'] = "N/A"
            else:
                schedule_map['last_run_at'] = str(periodic_task.last_run_at)
            
        else:
            schedule_map['enabled'] = "False"
            schedule_map['last_run_at'] = "N/A"
        
        schedule_maps[str(monitor_object.id)] = schedule_map
    
    context_dict['schedule_maps'] = schedule_maps
    return render(request, 'view_monitors.html', context_dict)

def monitor_run_result(request):
    context_dict = {} 
    if request.method == 'GET' and 'id' in request.GET:            
        try:
            Run_object = Run.objects.get(id=request.GET.get('id'))
        except Run.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Run doesn't exist")
            return render(request, 'monitor_run_result.html', context_dict) 
                     
        Monitor_object = Run_object.schedule
         
        if Monitor_object:
            operationRunList = OperationRun.objects.filter(run_id = request.GET.get('id'))
            operationRunDicList = []
            for operationRun in operationRunList:
                if operationRun.result:
                    result = operationRun.result.name
                else:
                    result = RunResult.NA

                operationRunDicList.append({'operationRunId': operationRun.id, 'name': Monitor_object.name, 'result': result})
            context_dict['operation_run_list'] = operationRunDicList 
            if Monitor_object.environment:
                context_dict['environment'] = Monitor_object.environment.name
          
    return render(request, 'monitor_run_result.html', context_dict)
def requestPopUp(request):
    context_dict = {}
    if 'id' in request.GET:
        OperationRunID = request.GET.get('id')
        try:
            operation_run = OperationRun.objects.get(id=OperationRunID)
        except:
            return render(request, 'requestPopup.html', context_dict)
        if operation_run.run and operation_run.run.schedule :
            monitor_schedule_object = operation_run.run.schedule
            context_dict['operationName'] = operation_run.run.schedule.name 
            context_dict['requestMessage'] = getRequestMsg(Constant.QA_MONITOR_LABEL, monitor_schedule_object.id)
    return render(request, 'requestPopup.html', context_dict)
def responsePopUp(request):
    context_dict = {}
    if 'id' in request.GET:
        OperationRunID = request.GET.get('id')
        try:
            operation_run = OperationRun.objects.get(id=OperationRunID)
        except:
            context_dict['responseMessage'] = ""
            context_dict['validationResult'] = ""
            return render(request, 'responsePopup.html', context_dict)
        context_dict['responseMessage'] = operation_run.responseMessage
        if operation_run.run and operation_run.run.schedule :
            context_dict['operationName'] = operation_run.run.schedule.name 
        validation_result = operation_run.validationResult

    context_dict['validationResult'] = StrUtil.validation_result_to_map(validation_result)
    return render(request, 'responsePopup.html', context_dict)
