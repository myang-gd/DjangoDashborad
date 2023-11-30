from django.conf import settings
from apps.qa_monitor.dto.result import Result
from apps.qa_monitor.util.mssql import Mssql
from apps.qa_monitor.models import Processor, SqlQuery, \
    Operation, WebServiceType, Cmd, IndividualServer
import importlib
from subprocess import Popen, PIPE, STDOUT
from common_utils.interpreter import Interpreter, Lexer
from common_utils.json_util import JsonUtil
from common_utils.xml_util import XmlUtil
import re
from collections import OrderedDict
from common_utils.constant import ResponseType, to_enum, OperationType ,\
    Constant, ValidationType
from common_utils.ws_util import WSUtil
import os
def process(processor_id, env_id, operation_id, server_id=None, surpass_msg=None, surpass_headers=None):    
    if processor_id and Processor.objects.filter(id=processor_id).exists():
        process_method = Processor.objects.get(id=processor_id).processMethod
        mod_name, func_name = process_method.rsplit('.',1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        return func(env_id, operation_id, server_id, surpass_msg, surpass_headers)
    else:
        print('Invalid processor id: ' + str(processor_id))
        return None
def jdbc_processor(env_id, operation_id, server_id=None, surpass_msg=None, surpass_headers=None): 
    print("Processing jdbc request id: " + str(operation_id))
    if operation_id and SqlQuery.objects.filter(id=operation_id).exists():
        query_obj = SqlQuery.objects.get(id=operation_id)
        if not check_environment(query_obj, env_id):
            return None
        sqlconn = query_obj.sqlconn
        query = query_obj.query
        validations = query_obj.validations
        if sqlconn and query and validations:
            return processJdbc(sqlconn.server, sqlconn.db, sqlconn.user, sqlconn.pwd, query, validations)
        else:
            print("sqlconn(%s)/query(%s)/validations(%s) have null values" %(str(sqlconn),str(query),str(validations)) )
def request_processor(env_id, operation_id, server_id=None, surpass_msg=None, surpass_headers=None): 
    print("Processing web service request id: " + str(operation_id))
    if operation_id and Operation.objects.filter(id=operation_id).exists():
        operation_object = Operation.objects.get(id=operation_id)
        if not check_environment(operation_object, env_id):
            return None
        if not operation_object.service:
            print("Operation object(id=%s) doesn't have service object" % str(operation_id))
            return None
        service_object = operation_object.service
        if surpass_msg:
            request_msg = surpass_msg
        else:
            request_msg = operation_object.requestMessage
        validation_type =(str(operation_object.validationType) if operation_object.validationType else ValidationType._PLAIN)
        if to_enum(operation_object.operationType, OperationType) == OperationType.PTS:
            service_obj = operation_object.service
            headers = WSUtil.get_header_dic(operation_object.headers)
            cert = os.path.join(settings.APP_FILE_ROOT , service_obj.cert) 
            key = os.path.join(settings.APP_FILE_ROOT , service_obj.key) 
            result = WSUtil.sendPTSRequest(service_obj.endpoint, request_msg, cert, key, headers)
        elif operation_object.webservicetype.name == WebServiceType.SOAP:
            result = WSUtil.processSoapRequest(getEndPointForEnv(operation_id,server_id), operation_object.name, service_object.port, request_msg, 
                                                                user=operation_object.username, password=operation_object.password, validations=operation_object.validations, vip_name=None)
        elif operation_object.webservicetype.name == WebServiceType.REST:
            if operation_object.method:
                method = str(operation_object.method)
            else:
                method = WSUtil.GET
            message_type = (str(operation_object.messageType) if operation_object.messageType else WSUtil.JSON)
            operation_object
            result = WSUtil.processRestRequest(url=getEndPointForEnv(operation_id,server_id), message=request_msg,
                                                                validations=operation_object.validations, headers=operation_object.headers, method=method, message_type=message_type, surpass_headers=surpass_headers,user=operation_object.username,password=operation_object.password)
        return parseRequestResult(result, operation_object.validations, validation_type)
    else:
        print("Operation object(id=%s) doesn't exist" % str(operation_id))
        return None

def cmd_processor(env_id, operation_id, server_id=None, surpass_msg=None, surpass_headers=None):
    print("Processing command line request id: " + str(operation_id))
    if operation_id and Cmd.objects.filter(id=operation_id).exists():
        operation_object = Cmd.objects.get(id=operation_id)
        if not check_environment(operation_object, env_id):
            return None
        script = operation_object.script
        validations = operation_object.validations
        if script and validations:
            return processCmd(script, validations)
        else:
            print("script(%s)/validations(%s) of Cmd have null values" %(str(script),str(validations)))

def check_environment(operation_object, env_id):
    if not operation_object:
        print("Operation_object is null")
        return False
    if not operation_object.environment or operation_object.environment.id != env_id:
        print("Invalid env_id: " + env_id + " or operation doesn't have environment")
        return False
    else:
        return True
        
def processJdbc(server, db, user, pwd, query, validations):
    result = Result()
    resList = ''
    validation_result_map = {}  
    success = settings.SUCCESS_N 
    try:
        mssql = Mssql(server=server, db=db, user=user, pwd=pwd)
        resList = mssql.ExecQuery(query)
    except Exception as e :
        success = settings.SUCCESS_N
        result.response = str(e)
    else:          
        result.response = JsonUtil.safe_dumps(getKeyValueForJdbc(resList, validations))
        success, validation_result_map = compositeValidate(result.response, validations) 
    finally:       
        result.success = success                 
        result.validationResultMap =  validation_result_map
        result.request = query
        return result 
def getKeyValueForJdbc(resList:[], validations):  
    responseType = ResponseType.toEnum(validations)
    new_list = []
    if resList and validations and responseType == ResponseType.key_value:
        for result in resList:
            if type(result) == type({}):
                new_dic = {}
                for key,value in result.items():
                    try:
                        new_dic[key] = XmlUtil.get_key_value_list(value)
                    except:
                        pass
                if new_dic:
                    new_list.append(new_dic)
    else:
        return  resList 
    
    return new_list
def processCmd(cmd, validations):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = p.stdout.read().decode(Constant.UTF8)
    result = Result()
    success, validation_result_map = compositeValidate(str(output), validations)    
    result.success = success
    result.error = ''
    result.response = str(output)
    result.validationResultMap = validation_result_map
    return result

def parseRequestResult(result_map, validations, validationType=None):
    result = Result()
    success, validation_result_map = compositeValidate(str(result_map[Constant.RESPONSE]), validations, validationType) 
    result.error = result_map[Constant.ERROR]
    result.response = result_map[Constant.RESPONSE]
    result.request = result_map[Constant.REQUEST]
    result.headers = (result_map[Constant.HEADERS] if Constant.HEADERS in result_map else None)
    result.validationResultMap = validation_result_map
    result.success = success
    return result

def compositeValidate(response, validations, validationType=None):
    responseType = ResponseType.toEnum(validations)
    lexer = Lexer(clearTerms(validations))
    interpreter = Interpreter(lexer, response, responseType,validationType=validationType)
    result_boolean = interpreter.expr()
#     interpreter.clear_vaditions(result_boolean)
    success = (settings.SUCCESS_Y if result_boolean else settings.SUCCESS_N)
    sortedMap = (OrderedDict(sorted(interpreter.validation_result_map.items())) if interpreter.validation_result_map else OrderedDict())
    return success,  sortedMap

def clearTerms(validations:str) -> str:    
    if not validations:
        return validations;
    for term in ResponseType.TERMs.value:
        validations = validations.replace(term,"") 
    return validations

def getEndPointForEnv(operation_id, server_id=None):
    endpoint = 'NotFound'
    if operation_id and Operation.objects.filter(id=operation_id).exists():
        operation_obj = Operation.objects.get(id=operation_id)
        if operation_obj.service:
            endpoint =  operation_obj.service.endpoint
        if operation_obj.vip and operation_obj.service and operation_obj.service.endpoint and operation_obj.environment:
            individual_server_list = IndividualServer.objects.filter(vip=operation_obj.vip, environment=operation_obj.environment)
            service_endpoint = operation_obj.service.endpoint
            if service_endpoint and individual_server_list:
                for individual_server_object in individual_server_list:
                    endpoint = re.sub('(https://)([^/]+)(/)', 'https://' + individual_server_object.ipAddress + '/', service_endpoint)
                    endpoint = re.sub('(http://)([^/]+)(/)', 'http://' + individual_server_object.ipAddress + '/', endpoint)
                    if server_id == individual_server_object.id:
                        break

    
    return endpoint
def getConnectionStrForEnv(operation_id):
    endpoint = 'NotFound'
    if operation_id and SqlQuery.objects.filter(id=operation_id).exists():
        operation_obj = SqlQuery.objects.get(id=operation_id)
        if operation_obj.sqlconn:
            endpoint = operation_obj.sqlconn.getConnectionStr()
        
    return endpoint
        
def getUrlForEnv(processor_id, operation_id, server_id=None):
    if processor_id and Processor.objects.filter(id=processor_id).exists() :
        processorObj = Processor.objects.get(id=processor_id)
        if processorObj.name == Constant.JDBC_PROC:
            return getConnectionStrForEnv(operation_id)
        elif processorObj.name == Constant.WS_PROC:
            return getEndPointForEnv(operation_id, server_id)
        else:
            return ''
    else:
        return ''