from celery import shared_task
from django.conf import settings
from apps.qa_monitor.models import Run, MonitorSchedule, RunResult, RunStatus, OperationRun, Operation, SqlQuery
from apps.qa_monitor.util.fw import FWUtil
from common_utils.processor import process, getUrlForEnv
from common_utils.json_util import JsonUtil
from common_utils.xml_util import XmlUtil, ModifySetting, AttributeType
from common_utils import processor
import logging
import traceback
from apps.qa_monitor.util.email_result import sendMonitorResult, sendMonitorResultWithResponse
from datetime import datetime, timedelta
from collections import deque
from django.core.cache import cache
import uuid
import json
import string, random
@shared_task
def processMonitors(run_context): 
    logger = logging.getLogger("qa_monitor")
    if type(run_context) == type({}):
        monitorId = run_context.get("monitorId")
        processorId = run_context.get("processorId")
        environmentId = run_context.get("environmentId")
        operationId = run_context.get("operationId")
        db_result = False
        
        try:
            schedule_object = MonitorSchedule.objects.get(id=monitorId)
            server_id = schedule_object.server.id if schedule_object.server else None
            
            surpass_msg = before_process(processorId, operationId, environmentId)
            header_map = before_process_header(processorId, operationId)
            result = process(processorId, environmentId, operationId, server_id, surpass_msg, header_map)
            
            
            if not result:
                print('result is null')
                return
            if not schedule_object:
                print('schedule_object is null')
                return
            else:
                schedule_object.latest_result = (RunResult.objects.get(name=RunResult.PASS) if result.success == result.SUCCESS_Y else 
                    RunResult.objects.get(name=RunResult.FAIL))
                schedule_object.save()
            if schedule_object and schedule_object.skip_success and result.success == settings.SUCCESS_Y:
                print('Skip publishing successful result for schedule %s' % (schedule_object.name))
                return
            
            db_result = schedule_object.store_result
            if db_result:
                run_object = Run.objects.create()
                run_object.schedule = schedule_object
                run_object.status = RunStatus.objects.get(name=RunStatus.RUNNING)
                run_object.result = RunResult.objects.get(name=RunResult.NA)  
                existingRunsCount = Run.objects.filter(schedule_id =monitorId).count() 
                run_object.name = schedule_object.name + "_Run_" + str(existingRunsCount + 1)
                run_object.save() 
                operationRun = OperationRun.objects.create();
                operationRun.save()
                operationRun.run = run_object
                
                if result.success == settings.SUCCESS_Y:
                    operationRun.result = RunResult.objects.get(name=RunResult.PASS)
                    run_object.result = RunResult.objects.get(name=RunResult.PASS)
                elif result.success == settings.SUCCESS_N:
                    operationRun.result = RunResult.objects.get(name=RunResult.FAIL)
                    run_object.result = RunResult.objects.get(name=RunResult.FAIL)
                operationRun.responseMessage =  result.response
                validationResultStr = JsonUtil.safe_dumps(result.validationResultMap)
                operationRun.validationResult =  validationResultStr
                operationRun.save() 
                run_object.status = RunStatus.objects.get(name=RunStatus.FINISHED)
                run_object.save()
            recipient_list = schedule_object.recipient_list
            if recipient_list and (result.success == settings.SUCCESS_N  or not schedule_object.skip_success ):
                if db_result:
                    sendMonitorResult(recipient_list, schedule_object.name, str(run_object.result), run_object.id)
                else:
                    run_result =(str(RunResult.objects.get(name=RunResult.FAIL)) if result.success == settings.SUCCESS_N else str(RunResult.objects.get(name=RunResult.PASS)))
                    url = getUrlForEnv(processorId, operationId, server_id)
                    key = "%s_%s_history_queue" % (str(processorId),str(operationId))
                    is_exceed_limit = checkHistory(key)
                    if is_exceed_limit:
                        logger.error("Skip to send mail for %s due to limit hit" % key)
                    else:
                        email_title = getCustomizedEmailTitle(title=schedule_object.email_title, name=schedule_object.name, env=str(schedule_object.environment)
                                                              ,result=run_result)
                        sendMonitorResultWithResponse(recipient_list, schedule_object.name_env(), run_result, result.response, result.validationResultMap, result.request, url, result.headers
                                                      ,email_title=email_title) 
        except:
            logger.error("Exception happened when processing monitor: " + str(run_context) + "\n" + traceback.format_exc()) 

def getCustomizedEmailTitle(**kwargs): 
    title = ''
    if 'title' in kwargs and kwargs.get('title'):
        title = kwargs.get('title')
        if 'name' in kwargs:
            title = title.replace('${NAME}', kwargs.get('name'))
        if 'env' in kwargs:
            title = title.replace('${ENV}', kwargs.get('env'))
        if 'result' in kwargs:
            title = title.replace('${RESULT}', kwargs.get('result'))
    
    return title
def before_process(processorId, operationId, env_id):
    request_msg = '';
    if str(processorId) == '2':
        if str(operationId) in ['46','47','48']:
            modify_date = datetime.today() - timedelta(days=5*30)
            end_date = modify_date + timedelta(days=5)
            start_year = modify_date.year
            start_month = modify_date.month
            start_day = modify_date.day
            
            end_year = end_date.year
            end_month = end_date.month
            end_day = end_date.day
            
            xpath_start_date_year = r"//v1:GetTransactionHistory//v11:StartDate/v12:YYYY"
            xpath_start_date_month = r"//v1:GetTransactionHistory//v11:StartDate/v12:MM"
            xpath_start_date_day = r"//v1:GetTransactionHistory//v11:StartDate/v12:DD"
            
            xpath_end_date_year = r"//v1:GetTransactionHistory//v11:EndDate/v12:YYYY"
            xpath_end_date_month = r"//v1:GetTransactionHistory//v11:EndDate/v12:MM"
            xpath_end_date_day = r"//v1:GetTransactionHistory//v11:EndDate/v12:DD"
            namespaces={"v11":"http://greendotcorp.com/processor/entity/transaction/message/v1","v1":"http://greendotcorp.com/processor/service/v1"
            ,"v12":"http://greendotcorp.com/shared/data/v1"}                            
            modify_list = []
            modify_list.append(ModifySetting(AttributeType.INNER_TEXT,xpath_start_date_year,namespaces,str(start_year)))
            modify_list.append(ModifySetting(AttributeType.INNER_TEXT,xpath_start_date_month,namespaces,str(start_month)))
            modify_list.append(ModifySetting(AttributeType.INNER_TEXT,xpath_start_date_day,namespaces,str(start_day)))
            
            modify_list.append(ModifySetting(AttributeType.INNER_TEXT,xpath_end_date_year,namespaces,str(end_year)))
            modify_list.append(ModifySetting(AttributeType.INNER_TEXT,xpath_end_date_month,namespaces,str(end_month)))
            modify_list.append(ModifySetting(AttributeType.INNER_TEXT,xpath_end_date_day,namespaces,str(end_day)))
            if Operation.objects.filter(id=operationId).exists():
                request_msg = XmlUtil.modify_elements_from_string(Operation.objects.get(id=operationId).requestMessage, modify_list)
        elif str(operationId) in ['79','81']:
            request_json =json.loads(Operation.objects.get(id=operationId).requestMessage)
            request_json['FirstName'] = ''.join(random.sample(string.ascii_lowercase, 10))
            request_json['LastName'] = ''.join(random.sample(string.ascii_lowercase, 10))
            request_msg = json.dumps(request_json, indent=4, sort_keys=True)
        elif str(operationId) in ['38','39','40']: #  PAL GetAccountDetails        
            namespaces={"v11":"http://greendotcorp.com/processor/entity/balance/message/v1","v1":"http://greendotcorp.com/processor/service/v1"
            ,"v12":"http://greendotcorp.com/shared/data/v1"}   
            result = processor.jdbc_processor(env_id, SqlQuery.objects.get(name="GetAccountReferenceIDFromNEC",environment__id=env_id).id);
            response = JsonUtil.safe_loads(result.response)
            if response and len(response) > 0 and 'AccountReferenceID' in response[0]:
                accountReferenceID = response[0]['AccountReferenceID']
                xpathAccountReferenceID = r"//v1:GetAccountDetails//v11:AccountReferenceID/v12:Value"
                modify_list = [ModifySetting(AttributeType.INNER_TEXT,xpathAccountReferenceID,namespaces,accountReferenceID)]
                if Operation.objects.filter(id=operationId).exists():
                    request_msg = XmlUtil.modify_elements_from_string(Operation.objects.get(id=operationId).requestMessage, modify_list)
        elif str(operationId) in ['83',]: #Transfers - P2P
            request_msg = FWUtil.changeTransfersP2PMessage(operationId, env_id)
    return request_msg;  
def before_process_header(processorId, operationId):
    header_map = {};
    if str(processorId) == '2':
        if str(operationId) in ['79','81','84','85']:
            header_map["RequestID"] = str(uuid.uuid1())
    return header_map
def checkHistory(key):
    result = False
    queue = cache.get(key)  
    if queue:
        now = datetime.now()
        count = sum(1 for i in list(queue) if (now - i).total_seconds() < 3600 )
        if count > 10:
            return True
        queue.append(datetime.now())
        cache.set(key, queue) 
    else:
        queue = deque( maxlen=20 )
        queue.append(datetime.now())
        cache.set(key, queue) 
    return result   
                                       