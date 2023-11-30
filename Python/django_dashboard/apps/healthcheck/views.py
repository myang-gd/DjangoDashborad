from django.shortcuts import render
from django.http.response import HttpResponse
from apps.healthcheck.models import  Environment, Vip , IndividualServer, Service, Operation , Team, ResponseAuditLogEntry, Schedule, Run, OperationRun,\
    RunResult
from djcelery.models import IntervalSchedule, CrontabSchedule
from django.core import serializers
from collections import OrderedDict 
import json
from django.db.models.functions import Lower
from django.forms.models import model_to_dict
import re
import logging
from datetime import datetime
from django.contrib import messages
from django.http import Http404
from xml.dom.minidom import parseString
from django.template.loader import render_to_string
from common_utils.jira import Jira
from common_utils.str_util import StrUtil
from common_utils.ws_util import WSUtil
from .api_runner_thread import APIRunnerThread
from common_utils.constant import Constant
import time
'''
How to iterate through dictionary and convert to JSON
for k, v in individual_server_by_vip_list.items():
    print("VIP is: " + k)
    jsonData = json.loads(v) # type is list
    for element in jsonData:
        print("Servers are " + element['fields']['name'])
'''   
   
def healthcheck(request, template="healthcheck.html"):
    logger = logging.getLogger("healthcheck")
    logger.info("Calling healthcheck request")
    if request.is_ajax() and 'environment' in request.GET and 'vip[]' in request.GET:
        environment = request.GET.get('environment')
        environmentObject = Environment.objects.filter(name=environment)
        vip = request.GET.getlist('vip[]')
        context_dict = OrderedDict()
        individual_server_filter_dict = OrderedDict()
        vipObjects = Vip.objects.filter(vipName__in=vip)
        operation_list = Operation.objects.filter(vip__in=vipObjects, environment=environmentObject)
        context_dict['team_list'] = get_teams_from_operations(operation_list)
        for vip_element in vip:
            vipObject = Vip.objects.filter(vipName=vip_element)
            individual_server_filter_list = IndividualServer.objects.filter(vip=vipObject, environment=environmentObject)
            individual_server_filter_list = serializers.serialize("json", list(individual_server_filter_list), fields=('name'))
            individual_server_filter_dict[vip_element] = individual_server_filter_list
        context_dict['individual_server_filter_dict'] = individual_server_filter_dict
        json_posts = json.dumps(context_dict)
        logger.info("Posting Json dump from ajax request (vip + environment): " + json_posts)
        return HttpResponse(json_posts, content_type='application/json')
    
    elif request.is_ajax() and 'environment' in request.GET:
        environment = request.GET.get('environment')
        environmentObject = Environment.objects.filter(name=environment)
        vip_list = Vip.objects.all()
        context_dict = OrderedDict()
        individual_server_filter_dict = OrderedDict()
        operation_list = Operation.objects.filter(vip__in=vip_list, environment=environmentObject)
        context_dict['team_list'] = get_teams_from_operations(operation_list)
        for vipObject in vip_list:
            individual_server_filter_list = IndividualServer.objects.filter(vip=vipObject, environment=environmentObject)
            individual_server_filter_list = serializers.serialize("json", list(individual_server_filter_list), fields=('name'))
            individual_server_filter_dict[vipObject.vipName] = individual_server_filter_list
        context_dict['individual_server_filter_dict'] = individual_server_filter_dict  
        json_posts = json.dumps(context_dict)
        logger.info("Posting Json dump from ajax request (environment): " + json_posts)
        return HttpResponse(json_posts, content_type='application/json')
    else:
        context_dict = get_base_data()
        logger.info("Non Ajax request (returning base context dictionary" + str(context_dict))
        return render(request, template , context_dict)
    
def get_teams_from_operations(operations):
    team_list = []
    for operation in operations:
        if operation.team is not None :
            team_list.append(operation.team.name)
    team_list = list(set(team_list))
    return team_list

def get_base_data():
    context_dict = {}
    environment_list = Environment.objects.all()
    vip_list = Vip.objects.all()
    operation_list = Operation.objects.filter(vip__in=vip_list, environment__in=environment_list)
    context_dict['team_list'] = get_teams_from_operations(operation_list)
    environment_server_dict = OrderedDict()
    for environment in environment_list:
        individual_server_filter_dict = OrderedDict()
        for vipObject in vip_list:
            individual_server_filter_list = IndividualServer.objects.filter(vip=vipObject, environment=environment)
            individual_server_filter_dict[vipObject.vipName] = individual_server_filter_list
        environment_server_dict[environment.name] = individual_server_filter_dict
    
    context_dict['environment_server_dict'] = environment_server_dict
    
    return context_dict

def get_all_servers(request, vip_display_name):
    logger = logging.getLogger("healthcheck")
    context_dict = {}
    environment_list = Environment.objects.all().order_by(Lower('name').desc())
    vip_object = Vip.objects.get(displayName=vip_display_name)
    environment_server_dict = OrderedDict()
    for environment in environment_list:
        individual_server_filter_dict = OrderedDict()
        individual_server_filter_list = IndividualServer.objects.filter(vip=vip_object, environment=environment)
        individual_server_filter_dict[vip_object.displayName] = individual_server_filter_list
        environment_server_dict[environment.name] = individual_server_filter_dict
      
    context_dict['environment_server_dict'] = environment_server_dict
    context_dict['vip_display_name'] = vip_display_name
    logger.info("Returning all server information" + str(context_dict))
    return render(request, 'get_all_servers.html', context_dict) 

def schedule(request):   
    
    return healthcheck(request,'schedule.html')

def schedule_run(request):
    logger = logging.getLogger("healthcheck")
    if request.is_ajax() and "run_id" in request.POST and 'operation' in request.POST:
        run_id = request.POST.get('run_id')
        operation = request.POST.get('operation')
        if run_id:
            run_obj =  Run.objects.get(id=run_id)
            if run_obj:
                if operation == 'cancel':
                    run_obj.needCancel = True
                    run_obj.save()
                elif operation == 'remove':
                    run_obj.delete()
        json_posts = json.dumps({'success' : 'Y'})
        return HttpResponse(json_posts, content_type='application/json')
    else:
        
        context_dict = {}
        schedule_run_map = OrderedDict()
        
        if 'sid' in request.GET:
            ScheduleList = Schedule.objects.filter(id=request.GET.get('sid'))
        else: 
            ScheduleList = Schedule.objects.all()
        if ScheduleList:
            for schedule in ScheduleList:
                if not request.user ==  schedule.owner and not request.user.is_superuser :
                    continue
                runs = []
                operation_count = 0
          
                vip_server_operation_map = get_vip_server_operation_map_by_schedule(schedule.id, None)
                if vip_server_operation_map and 'operation_count' in vip_server_operation_map:
                    operation_count = vip_server_operation_map.get('operation_count')
                for run in Run.objects.filter(schedule=schedule).order_by('-startDate'):
                    run_fields = model_to_dict(run, fields=[field.name for field in run._meta.fields])
                    run_fields['status_name'] = run.status.name
                    run_fields['result_name'] = run.result.name
                    if operation_count != 0:
                        run_fields['pass_rate'] = int(OperationRun.objects.filter(run=run,result=RunResult.objects.get(name=RunResult.PASS)).count()/operation_count*100.0)
                    else:
                        run_fields['pass_rate'] = '0'
                    runs.append(run_fields)
                schedule_run_map[schedule.name] = runs
        context_dict['schedule_run_map'] = schedule_run_map
        logger.info("Non Ajax request (returning base context dictionary" + str(context_dict))
        return render(request, 'schedule_run.html' , context_dict)

def schedule_views(request):
    context_dict = {}
    schedule_maps = OrderedDict()
    for schedule_object in Schedule.objects.exclude(name__isnull=True):    
        if not request.user ==  schedule_object.owner and not request.user.is_superuser :
            continue
        schedule_map = OrderedDict()
        schedule_map['name'] = schedule_object.name
        schedule_map['id'] = schedule_object.id
          
        if schedule_object.owner :
            schedule_map['owner'] = schedule_object.owner.username
        else:
            schedule_map['owner'] = "N/A"
        if schedule_object.environment :
            schedule_map['environment'] = schedule_object.environment.name
        else:
            schedule_map['environment'] = "N/A"
        if schedule_object.periodic_task :
            schedule_map['enabled'] = str(schedule_object.periodic_task.enabled)
            if not schedule_object.periodic_task.last_run_at:
                schedule_map['last_run_at'] = "N/A"
            else:
                schedule_map['last_run_at'] = str(schedule_object.periodic_task.last_run_at)
            
        else:
            schedule_map['enabled'] = "False"
            schedule_map['last_run_at'] = "N/A"
        
        schedule_maps[str(schedule_object.id)] = schedule_map
    
    context_dict['schedule_maps'] = schedule_maps
    return render(request, 'schedule_views.html', context_dict) 

def get_interval_cron(context_dict):
    if type(context_dict) != type({}):
        return
    intervalList = []
    for interval in IntervalSchedule.objects.all():
        interval_fields = model_to_dict(interval, fields=[field.name for field in interval._meta.fields])
        interval_fields["display_name"] = 'every %d  %s' % (interval.every, interval.period) 
        intervalList.append(interval_fields)
    context_dict['interval_list'] = intervalList
    cronList = []
    for cron in CrontabSchedule.objects.all():
        cron_fields = model_to_dict(cron, fields=[field.name for field in cron._meta.fields])
        cron_fields["display_name"] = '%s %s %s %s %s (m/h/d/dM/MY)' % (cron.minute, cron.hour, cron.day_of_week, cron.day_of_month, cron.month_of_year) 
        cronList.append(cron_fields)
    context_dict['cron_list'] = cronList

def get_vip_server_operation_map(environment, vipList, individualServerList, teamList, selectedOperationList = None, run_id = None):   
    environmentObject = Environment.objects.filter(name=environment)
    if teamList:
        teamObjects = Team.objects.filter(name__in=teamList)
    else:
        teamObjects = []
    vip_server_operation_map = OrderedDict()
    operation_count = 0
    if not vipList:
        return vip_server_operation_map
    for vipName in vipList:
        vipObject = Vip.objects.get(vipName=vipName)
        if len(teamObjects) > 0:
            operation_list = Operation.objects.filter(environment=environmentObject, vip=vipObject, team__in=teamObjects)
        else:
            operation_list = Operation.objects.filter(environment=environmentObject, vip=vipObject)
        
        if selectedOperationList:
            operation_list = [operation for operation in operation_list if operation.id in selectedOperationList]
        if operation_list:
            operation_count += len(operation_list)
        individual_server_list = IndividualServer.objects.none()
        
        # We need to determine list of IP addresses so we can populate entry in table.
        # If user did not pass any individual server, it means that we want to give option to run on all individual servers assigned to given VIP
        # If user pass individual server(s), then we want to filter out only these individual servers
        if (len(individualServerList) == 0):
            individual_server_list = IndividualServer.objects.filter(vip=vipObject, environment=environmentObject)
        else:
            for individualServer in individualServerList:
                individual_server_object = IndividualServer.objects.filter(environment=environmentObject, vip=vipObject, name=individualServer)
                individual_server_list = individual_server_list | individual_server_object
            
        server_operation_map = {}
        for operation in operation_list:
            if not operation.timeout:
                operation.timeout = 10 
            operation_fields = model_to_dict(operation, fields=[field.name for field in operation._meta.fields if field.name != 'validations'])
            if operation.team is not None:
                teamname = operation.team.name
            else:
                teamname = 'N/A'
              
            if run_id :
                try:
                    operation_run = OperationRun.objects.get(run_id=run_id, operation = operation) 
                    operation_fields["run_result"] = operation_run.result.name
                    operation_fields[Constant.ELAPSED] = (str(operation_run.elapsed) if operation_run.elapsed else 'N/A')
                except:
                    operation_fields["run_result"] = "N/A"
                   

                    
            service_object = Service.objects.get(id=operation.service.id)
            service_fields = model_to_dict(service_object, fields=[field.name for field in service_object._meta.fields if field.name != 'name' and field.name != 'id']) # We dont need serice name since it is stored as key in dictionary
            service_operation_field = operation_fields.copy()
            
            service_operation_field.update(service_fields)
            service_operation_field['teamname'] = teamname
           

            for individual_server_object in individual_server_list:
                # Since SerivceName is servered as Key for table in HTML - which means different "ServiceName" will corresponse to different record in table. 
                # and since we want to be able to execute same service on multiple individual servers, we add individual server name to servic name in parantheses to ensure new
                # td row is generated in html file
                serviceName = operation.service.name + '_('  + individual_server_object.name  + ')'
                service_object.endpoint = re.sub('(http://)([^/]+)(/)', 'http://' + individual_server_object.ipAddress + '/', service_object.endpoint)
                service_object.endpoint = re.sub('(https://)([^/]+)(/)', 'https://' + individual_server_object.ipAddress + '/', service_object.endpoint)
                service_fields = model_to_dict(service_object, fields=[field.name for field in service_object._meta.fields if field.name != 'name' and field.name != 'id']) # We dont need serice name since it is stored as key in dictionary
                service_operation_field = operation_fields.copy()
                service_operation_field.update(service_fields)
                service_operation_field['teamname'] = teamname
                if serviceName in server_operation_map:
                    server_operation_map.get(serviceName).append(service_operation_field)
                else:
                    server_operation_map[serviceName] = [service_operation_field]            
        
        vip_server_operation_map[vipName] = server_operation_map
    vip_server_operation_map['operation_count'] = operation_count   
    return vip_server_operation_map
def get_vip_server_operation_map_by_schedule(Schedule_id, Run_id):
    Schedule_object = Schedule.objects.get(id=Schedule_id)
    
    if Schedule_object.periodic_task:
        args = Schedule_object.periodic_task.args
        args_json = json.loads(args)[0]
        if args_json:
            operationList = args_json.get('operationList')
            environment = args_json.get('environment')
            vip = args_json.get('vip')
            individualServer = args_json.get('individualServer')
            team = args_json.get('team')
    
    return get_vip_server_operation_map(environment, vip, individualServer, team, operationList, Run_id)
    
def schedule_config(request):
    logger = logging.getLogger("healthcheck")
    context_dict = get_base_data();
    vip_server_operation_map = OrderedDict()
    if request.is_ajax():
        if request.method == 'POST' and 'remove' in request.POST :
            schedule_id = request.POST.get('schedule_id')
            Schedule_object = Schedule.objects.get(id=schedule_id)
            if Schedule_object:
                Schedule_object.terminate()
                json_posts = json.dumps({'success' : 'Y'})
            else:
                json_posts = json.dumps({'success' : 'N', 'error': "Schedule doesn't exist"})
            return HttpResponse(json_posts, content_type='application/json')   
        elif request.method == 'POST' : 
            environment = request.POST.get('environment') 
            vip= json.loads(request.POST.get('vip').replace("'", '"' ))
            individualServer = json.loads(request.POST.get('individualServer').replace("'", '"' ))
            team = json.loads(request.POST.get('team').replace("'", '"' ))          

            operationList = []
            if 'operationList[]' in request.POST:
                operationList = request.POST.getlist('operationList[]')
            schedule_name = request.POST.get('schedule_name')
            schedule_desc = request.POST.get('schedule_desc')
            threshold = request.POST.get('threshold')
            interval_id = request.POST.get('interval_id')
            cron_id = request.POST.get('cron_id')
            enabled = (request.POST.get('enabled') == 'TRUE')
            enable_run_log = (request.POST.get('enable_run_log') == 'TRUE')
            environment_name = request.POST.get('environment')
            try:
                environment_obj =  Environment.objects.get(name=environment_name)
            except:
                raise Http404("Environment %s does not exist" % (environment_name) )
             
             
            operationDicList = []
            for op in operationList:
                operationDicList.append(json.loads(op))
             
            if "schedule_id" in request.POST:
                schedule_id = request.POST.get('schedule_id')
                Schedule_object = Schedule.objects.get(id=schedule_id)
            else: 
                Schedule_object = Schedule.objects.create(name = str(schedule_name), description = str(schedule_desc))
                Schedule_object.save()
                if request.user:
                        Schedule_object.owner = request.user
                
            if Schedule_object:    
                Schedule_object.name = schedule_name
                Schedule_object.description = schedule_desc
                Schedule_object.enable_run_log = enable_run_log
                try:
                    threshold_int = int(threshold) 
                except:
                    if not threshold:
                        Schedule_object.threshold = None
                    pass
                else:                   
                    Schedule_object.threshold = threshold_int
                Schedule_object.environment = environment_obj
                Schedule_object.save()
                data = [{"operationList" : operationDicList,
                      "scheduleId" : Schedule_object.id,
                      "environment" : environment,
                      "vip" : vip ,
                      "individualServer" : individualServer,
                      "team" : team
                }]
                Schedule_object.schedule_edit_every(schedule_name, "apps.healthcheck.tasks.processRequests", enabled, interval_id, cron_id, json.dumps(data))
                json_posts = json.dumps({'success' : 'Y'})              
            else:
                json_posts = json.dumps({'success' : 'N'})  
        return HttpResponse(json_posts, content_type='application/json')
    elif request.method == 'GET' and 'id' in request.GET :
        try:
            Schedule_object = Schedule.objects.get(id=request.GET.get('id'))
        except Schedule.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Schedule doesn't exist")
            return render(request, 'schedule_config.html', context_dict)         
        
        if Schedule_object.periodic_task: 
            if Schedule_object.periodic_task.interval:
                context_dict['interval_id'] = Schedule_object.periodic_task.interval.id
            if Schedule_object.periodic_task.crontab:
                context_dict['cron_id'] = Schedule_object.periodic_task.crontab.id      
            context_dict['enabled'] =   Schedule_object.periodic_task.enabled
        
        get_interval_cron(context_dict)
        
        environment = ""
        
        context_dict['vip_server_operation_map'] = get_vip_server_operation_map_by_schedule(request.GET.get('id'), None)
        context_dict['schedule_name'] = Schedule_object.name
        context_dict['schedule_id'] = Schedule_object.id
        context_dict['schedule_desc'] = Schedule_object.description
        context_dict['enable_run_log'] = bool(Schedule_object.enable_run_log)
        if Schedule_object.threshold is not None:
            context_dict['schedule_threshold'] = Schedule_object.threshold
        if Schedule_object.environment:
            context_dict['environment'] = Schedule_object.environment.name
        periodic_task_args = json.loads(Schedule_object.periodic_task.args)[0]
        context_dict['individualServer'] = periodic_task_args.get('individualServer')
        context_dict['vip'] = periodic_task_args.get('vip')
        context_dict['team'] = periodic_task_args.get('team')
        if Schedule_object.owner:
            context_dict['schedule_owner'] = Schedule_object.owner.username
        logger.info("Returning Json Dump from result (Non-Ajax)" + json.dumps(vip_server_operation_map))
        return render(request, 'schedule_config.html', context_dict)
    
    elif request.method == 'POST' and 'environment' in request.POST :
        if "schedule_name" in request.POST:
            context_dict["schedule_name"] = request.POST['schedule_name']
        if "schedule_desc" in request.POST:
            context_dict["schedule_desc"] = request.POST['schedule_desc']
        if "schedule_id" in request.POST:
            context_dict["schedule_id"] = request.POST['schedule_id']
        if "schedule_enable" in request.POST:
            context_dict["enabled"] = request.POST['schedule_enable']
        if "schedule_owner" in request.POST:
            context_dict["schedule_owner"] = request.POST['schedule_owner']
        if "crontab" in request.POST:
            context_dict["cron_id"] = request.POST['crontab'] 
        if "interval" in request.POST:
            context_dict["interval_id"] = request.POST['interval']     

        get_interval_cron(context_dict)
        environment = request.POST['environment']
        individualServerList = request.POST.getlist('individualServer', []) # Individual server can be empty if user decided to run on VIPs only
        vipList = request.POST.getlist('vip')
        teamList = request.POST.getlist('team')
        context_dict['vip_server_operation_map'] = get_vip_server_operation_map( request.POST['environment'], request.POST.getlist('vip'), request.POST.getlist('individualServer', []), request.POST.getlist('team'),None)

            
        context_dict['environment'] = environment
        context_dict['individualServer'] = individualServerList
        context_dict['vip'] = vipList
        context_dict['team'] = teamList
        
        logger.info("Returning Json Dump from result (Non-Ajax)" + json.dumps(vip_server_operation_map))
        return render(request, 'schedule_config.html', context_dict) 
    else:
        return render(request, 'schedule_config.html', context_dict)  
def schedule_run_result(request):
    context_dict = {};
    
    if request.method == 'GET' and 'id' in request.GET:            
        try:
            Run_object = Run.objects.get(id=request.GET.get('id'))
        except Run.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Run doesn't exist")
            return render(request, 'schedule_run_result.html', context_dict) 
                    
        Schedule_object = Run_object.schedule
        
        if Schedule_object:
            context_dict['vip_server_operation_map'] = get_vip_server_operation_map_by_schedule(Schedule_object.id,Run_object.id) 
            if Schedule_object.environment:
                context_dict['environment'] = Schedule_object.environment.name
        context_dict['run_id'] = request.GET.get('id')
        
        return render(request, 'schedule_run_result.html', context_dict)
    
def is_alive(thread):
    is_alive = False
    try:
        is_alive=thread.is_alive()
    except:
        return False
    else:
        return is_alive
def result(request):
    logger = logging.getLogger("healthcheck")
    if request.is_ajax() and 'operation_id' in request.GET and 'endpoint' in request.GET:
        operation_object = Operation.objects.get(id=request.GET.get('operation_id'))
        service_object = Service.objects.get(id=operation_object.service.id)
        endpoint = request.GET.get('endpoint')
        vip_name = None
        if operation_object.vip and operation_object.vip.vipName in (Vip.SOACOM,Vip.COM):
            vip_name = operation_object.vip.vipName

        runnerThread = APIRunnerThread(model_to_dict(operation_object), model_to_dict(service_object), endpoint, vip_name)
        runnerThread.start()
        startTime = time.time()
        timeout = ( operation_object.timeout if  operation_object.timeout else 10)

        result = {Constant.SUCCESS: Constant.N, Constant.ERROR: "No result", Constant.RESPONSE: "No result",
                                     Constant.ELAPSED: "N/A"}
        time_elapse = 0
        is_timeout = False
        while is_alive(runnerThread):
            time_elapse = time.time() - startTime
            if runnerThread.getResult():
                result = runnerThread.getResult()
                runnerThread.terminate()
                break
            if time_elapse >= timeout:
                is_timeout = True
                runnerThread.terminate()
                break;
            time.sleep(1) 
        if is_timeout:
            json_posts = json.dumps({Constant.SUCCESS: Constant.N, Constant.ERROR: "", Constant.RESPONSE: "Time out(%s seconds)" %str(timeout),
                                     Constant.ELAPSED: str(round(time_elapse,2)) + "s"})  
        else:
            result[Constant.ELAPSED] = str(round(time_elapse,2)) + "s"
            json_posts = json.dumps(result)
            
                
#         json_posts = getServiceResult(request.GET.get('operation_id'), endpoint)
#         i = datetime.now()
#         
#         ResponseAuditLogEntry.objects.create(service=service_object, user=request.user, operation=operation_object, 
#                                              responseMessage=result['response'], validationResult=result['validationResult'],
#                                              date=i.strftime('%Y-%m-%d'), time=i.strftime('%H:%M:%S'))

        logger.info("Returning Json Dump from result (ajax)" + json_posts) 
        return HttpResponse(json_posts, content_type='application/json')

    context_dict = get_base_data();

    vip_server_operation_map = OrderedDict()
    
    if request.method == 'POST':
        environment = request.POST['environment']
        individualServerList = request.POST.getlist('individualServer', []) # Individual server can be empty if user decided to run on VIPs only
        vipList = request.POST.getlist('vip')
        teamList = request.POST.getlist('team')
        vip_server_operation_map = get_vip_server_operation_map(environment, vipList, individualServerList, teamList)
                    
        context_dict['environment'] = environment
        context_dict['vip_server_operation_map'] = vip_server_operation_map
        logger.info("Returning Json Dump from result (Non-Ajax)" + json.dumps(vip_server_operation_map))
        return render(request, 'result.html', context_dict) 
    
def requestPopUp(request):
    logger = logging.getLogger("healthcheck")
    context_dict = {}
    operationId = request.GET['operationId']
    operationObj = Operation.objects.get(id=operationId)
    try:
        context_dict['requestMessage'] = parseString(operationObj.requestMessage).toprettyxml()
    except:
        context_dict['requestMessage'] = operationObj.requestMessage
    context_dict['operationName']  = operationObj.name
    logger.info("Returning Json dump from request message pop up" + json.dumps(context_dict))
    return render(request, 'requestPopup.html', context_dict)

def responsePopUp(request):
    context_dict = {}
    logger = logging.getLogger("healthcheck")
    if 'operationId' in request.GET:
        operationId = request.GET.get('operationId', False)
        context_dict['operationName'] = Operation.objects.get(id=operationId).name
    if 'runId' in request.GET and 'operationId' in request.GET:
        runId = request.GET.get('runId')
        try:
            operation_run = OperationRun.objects.get(run_id=runId, operation_id=operationId)
        except:
            context_dict['responseMessage'] = ""
            context_dict['validationResult'] = ""
            return render(request, 'responsePopup.html', context_dict)
        context_dict['responseMessage'] = operation_run.responseMessage
        validation_result = operation_run.validationResult

             
    if request.method == 'POST' and 'operation_id' in request.POST and 'response' in request.POST and 'validation_result' in request.POST:
        context_dict['responseMessage'] = request.POST.get('response')
        validation_result = request.POST.get('validation_result')
        operationId = request.GET.get('operationId', False)
        if operationId and Operation.objects.filter(id=operationId).exists():
            context_dict['operationName'] = Operation.objects.get(id=operationId).name

    context_dict['validationResult'] = StrUtil.validation_result_to_map(validation_result)
    logger.info("Returning Json dump from response message pop up" + json.dumps(context_dict))
    if request.method == 'POST' and 'operation_id' in request.POST and 'response' in request.POST and 'validation_result' in request.POST:
        html = render_to_string('responsePopup.html', context_dict)
        return HttpResponse(json.dumps({'html': html}), content_type='application/json')
    else:   
        return render(request, 'responsePopup.html', context_dict)

def action_change(request):
    vip_name = ""
    if request.method == 'GET' and 'vip_id' in request.GET:
        vip_id =  request.GET.get('vip_id')        
        if vip_id and Vip.objects.filter(id=vip_id).exists():
            vip_name = Vip.objects.get(id=vip_id).vipName
            if vip_name not in (Vip.SOACOM,Vip.COM):
                vip_name = ""
    json_posts = json.dumps({'vip_name' : vip_name})              
          
    return HttpResponse(json_posts, content_type='application/json')
def operation_save_check(request):
    not_valid = []
    not_approve = []
    if request.method == 'GET' and 'tickets' in request.GET and 'check_approve' in request.GET:
        ticket_numbers =  request.GET.get('tickets')  
        check_approve =  request.GET.get('check_approve')
        for ticket_number in ticket_numbers.split(","):
            if ticket_number:
                if not Jira.instance().isValid(ticket_number):
                    not_valid.append(ticket_number)
                elif check_approve and not Jira.instance().isApproved(ticket_number):
                    not_approve.append(ticket_number)      
    json_posts = json.dumps({'not_valid' : not_valid, 'not_approve' : not_approve})              
          
    return HttpResponse(json_posts, content_type='application/json')