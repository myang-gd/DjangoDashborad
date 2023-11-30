from celery import shared_task
from apps.healthcheck.models import  Service, Operation , OperationRun, Run, Schedule, RunResult, RunStatus, Vip, WebServiceType
from apps.healthcheck.views import get_vip_server_operation_map
from common_utils.io_util import FileUtil 
from common_utils.ws_util import WSUtil
from django_dashboard import settings
import time
import logging
@shared_task
def processRequests(run_context): 
    logger = logging.getLogger("healthcheck")
    try:
        if type(run_context) == type({}):
            operation_list = run_context.get("operationList")
            scheduleId = run_context.get("scheduleId")
            vip = run_context.get("vip")
            individualServer = run_context.get("individualServer")
            team = run_context.get("team")
            environment = run_context.get("environment")
            
            vip_server_operation_map = get_vip_server_operation_map(environment, vip, individualServer, team, operation_list)     
            
            run_object = Run.objects.create()
            run_object.schedule = Schedule.objects.get(id=scheduleId)
            run_object.status = RunStatus.objects.get(name=RunStatus.RUNNING)
            run_object.result = RunResult.objects.get(name=RunResult.NA)
            existingRunsCount = Run.objects.filter(schedule_id =scheduleId).count()
            if Run.objects.filter(schedule_id =scheduleId).exists():
                    existingIndexStr = Run.objects.filter(schedule_id =scheduleId).order_by('name').last().name.split('_')[-1]
                    if existingIndexStr.isdigit():
                        existingRunsCount = int(existingIndexStr)
    
            run_object.name = Schedule.objects.get(id=scheduleId).name + "_Run_" + str(existingRunsCount + 1)
            run_object.save() 
            for  key, value in vip_server_operation_map.items():
                if value and type(value) == type({}):
                    for key, value in value.items():
                        if value and type(value) == type([]):
                            for operation in value:
                                run_object = Run.objects.get(id=run_object.id)
                                if run_object.needCancel:
                                    break
                                if(type(operation) == type({})):
                                    operation_object = Operation.objects.get(id=operation.get('id'))
                                    vip_name = None
                                    if operation_object.vip and operation_object.vip.vipName in (Vip.SOACOM,Vip.COM):
                                        vip_name = operation_object.vip.vipName
                                    service_object = Service.objects.get(id=operation.get('service'))
                                    endpoint = operation.get('endpoint')
                                    operationRun = OperationRun.objects.create();
                                    operationRun.save()
                                    operationRun.operation = operation_object
                                    operationRun.service = service_object
                                    operationRun.run = run_object
                                    startTime = time.time()
                                    timeout = ( operation_object.timeout if  operation_object.timeout else 10)
                                    if operation_object.webservicetype.name == WebServiceType.SOAP:
                                        result = WSUtil.processSoapRequest(endpoint, operation_object.name, service_object.port, operation_object.requestMessage, 
                                                                    user=operation_object.username, password=operation_object.password, validations=operation_object.validations, vip_name=vip_name,timeout=timeout)
                                    elif operation_object.webservicetype.name == WebServiceType.REST:
                                        result = WSUtil.processRestRequest(url=endpoint, message=operation_object.requestMessage,
                                                                    validations=operation_object.validations, headers=operation_object.headers,timeout=timeout)
                                    if result is not None:
                                        if result.get('success') == settings.SUCCESS_Y:
                                            operationRun.result = RunResult.objects.get(name=RunResult.PASS)
                                        elif result.get('success') == settings.SUCCESS_N:
                                            operationRun.result = RunResult.objects.get(name=RunResult.FAIL)
                                        operationRun.responseMessage =  result.get('response')
                                        operationRun.validationResult =  result.get('validationResult')
                                        operationRun.elapsed = round(time.time()-startTime,2)
                                    operationRun.save() 
                        
            operation_count = 0
            pass_rate = 0
            if vip_server_operation_map and 'operation_count' in vip_server_operation_map:
                operation_count = vip_server_operation_map.get('operation_count')
            if operation_count != 0:
                pass_rate = int(OperationRun.objects.filter(run=run_object,result=RunResult.objects.get(name=RunResult.PASS)).count()/operation_count*100.0)
            if run_object.needCancel:
                run_object.status = RunStatus.objects.get(name="Canceled")                             
            else:
                run_object.status = RunStatus.objects.get(name="Finished")
            if run_object.schedule:
                if run_object.schedule.threshold == None:
                    threshold = Schedule._meta.get_field('threshold').get_default()
                else:
                    threshold = run_object.schedule.threshold
                if pass_rate >= threshold:
                    run_object.result = RunResult.objects.get(name=RunResult.PASS)
                else:
                    run_object.result = RunResult.objects.get(name=RunResult.FAIL) 
            run_object.save() 
            if run_object and run_object.schedule and run_object.schedule.enable_run_log and run_object.status:
                FileUtil.appendtoFile(settings.RUN_LOG_PATH, '%s    %s    %s    %s    %s    %s' %(run_object.schedule.name, run_object.name, run_object.startDate.strftime("%Y-%m-%d %H:%M:%S"), 
                                                                                            run_object.status.name, str(pass_rate), run_object.result.name))
    except Exception as e:
        logger.error('Failed to processRequests run_context %s error: ' % str(run_context), str(e))