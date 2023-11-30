#auth/views.py

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.backends import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import *
import requests
import xmltodict
import json
from django import forms
from suds.client import Client
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, time
from _overlapped import NULL
import types


cfsUrl = 'http://gdcqatools01:82/CustomerFinderService/CustomerFinderService.svc?wsdl'
dmsUrl = 'http://gdcqatools01:82/DataMonitorService/DataMonitorService.svc?wsdl'


def testdata_monitor(request):
    
    isadmin = request.user.has_perm('customerFinder.configure_customer_finder')
    userName = request.user.username
    userinfo = {'isadmin' : isadmin, 'userName' : str(userName).lower()}
    
    monitor_List = []
    monitor = {}

    client = Client(dmsUrl, retxml = True)

    monitors = client.service.GetExsitingMonitors()

    results =  xmltodict.parse(monitors)

    data = json.loads(json.dumps(results))

    datalist = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:monitorList']['b:Monitor']
    
    message = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:responseCode']     

    if responseCode == 'Success':

        for list in datalist:
            id = list['b:id']
            name = list['b:name']
            description = list['b:description']
            appendQueryClause = list['b:appendQueryClause']
            createBy = list['b:createBy']
            emailPrefix = list['b:emailPrefix']
            environmentId = list['b:environmentId']
            environmentName = list['b:environmentName']
            intervalDays = list['b:intervalDays']
            isIPS = list['b:isIPS']
            multipleLayer = list['b:multipleLayer']
            productCode = list['b:productCode']
            projectId = list['b:projectID']
            projectName = list['b:projectName']
            scheduledStartTime = list['b:scheduledStartTime']
            userIDPrefix = list['b:userIDPrefix']
            
            monitor = {"id": str(id), "name" : name, "description" : description, "appendQueryClause" : appendQueryClause, "createBy" : str(createBy).lower(),
                       "emailPrefix" : emailPrefix, "environmentId" : str(environmentId), "environmentName" : environmentName, "intervalDays" : intervalDays, "isIPS" : str(isIPS), "multipleLayer" : str(multipleLayer), "productCode" : str(productCode),
                       "projectId" : str(projectId), "projectName" : projectName, "scheduledStartTime" : str(scheduledStartTime), "userIDPrefix" :userIDPrefix}

            monitor_List.append(monitor)

    else:
        
        errorReason = {"message" : message}                    

        monitor_List.append(errorReason)
    
    return render(request, 'testdata_monitor_home.html', {'userinfo' : userinfo, "active_monitors" : monitor_List})


def testdata_monitor_runs(request, monitor_id):
    
    isadmin = request.user.has_perm('customerFinder.configure_customer_finder')
    userName = request.user.username
    userinfo = {'isadmin' : isadmin, 'userName' : str(userName).lower()}
    
    isNoReslut = True
    run_List = []
    run = {}
    datalist = []

    client = Client(dmsUrl, retxml = True)

    runs = client.service.GetRunsByMonitorIdService(monitor_id)

    results =  xmltodict.parse(runs)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['GetRunsByMonitorIdServiceResponse']['GetRunsByMonitorIdServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetRunsByMonitorIdServiceResponse']['GetRunsByMonitorIdServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetRunsByMonitorIdServiceResponse']['GetRunsByMonitorIdServiceResult']['a:responseCode']     
    
    
    try: 
        if data['s:Envelope']['s:Body']['GetRunsByMonitorIdServiceResponse']['GetRunsByMonitorIdServiceResult']['a:runList']['b:Run'] != None:
            isNoReslut = False
    except KeyError:
        pass
    
    if isNoReslut == False:
        datalist = data['s:Envelope']['s:Body']['GetRunsByMonitorIdServiceResponse']['GetRunsByMonitorIdServiceResult']['a:runList']['b:Run']
    
    if responseCode == 'Success':
        if isNoReslut == False:
            if str(type(datalist)) == "<class 'list'>":
                for list in datalist:
                    monitorId = list['b:monitorId']
                    id = list['b:id']
                    monitorName = list['b:monitorName']
                    name = list['b:name']
                    description = list['b:description']
                    finishDate = list['b:finishDate']
                    startDate = list['b:startDate']
                    statusName = list['b:statusName']
                    status = list['b:status']
                    requestBy = list['b:requestBy']
                    
                    if str(type(startDate)) == "<class 'dict'>":
                        startDate = ""
                    
                    if str(type(finishDate)) == "<class 'dict'>":
                        finishDate = ""
            
                    run = {"id": str(id), "name" : name, "monitorId" : str(monitorId), "monitorName" : monitorName, "description" : description, "finishDate" : str(finishDate),
                                      "startDate" : str(startDate), "statusName" : statusName, "status" : status, "requestBy" : requestBy}

                    run_List.append(run)
            else:
                monitorId = datalist['b:monitorId']
                id = datalist['b:id']
                monitorName = datalist['b:monitorName']
                name = datalist['b:name']
                description = datalist['b:description']
                finishDate = datalist['b:finishDate']
                startDate = datalist['b:startDate']
                statusName = datalist['b:statusName']
                status = datalist['b:status']
                requestBy = datalist['b:requestBy']
                
                if str(type(startDate)) == "<class 'dict'>":
                    startDate = ""
                    
                if str(type(finishDate)) == "<class 'dict'>":
                    finishDate = ""
            
                run = {"id": str(id), "name" : name, "monitorId" : str(monitorId), "monitorName" : monitorName, "description" : description, "finishDate" : str(finishDate), 
                       "startDate" : str(startDate), "statusName" : statusName, "status" : status, "requestBy" : requestBy}

                run_List.append(run)
        else:
            run = {"id": "", "name" : "", "monitorId" : "", "monitorName" : "", "description" : "", "finishDate" : "", 
                   "startDate" : "", "statusName" : "", "status" : "", "requestBy" : ""}

            run_List.append(run)
    else:
        
        errorReason = {"message" : message}

        run_List.append(errorReason)
        
        
        
    isNoReslut_2 = True
    monitormapping_List = []
    monitormapping = {}
    datalist_2 = []
   
    client = Client(dmsUrl, retxml = True)
    
    custTypes = client.service.GetMonitorDetails(monitor_id)

    results =  xmltodict.parse(custTypes)

    data = json.loads(json.dumps(results))
    
    parent_monitorName = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:name']
    parent_monitorCreateBy = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:createBy']
    parent_monitor = {"parent_monitorId" : str(monitor_id), "parent_monitorName" : parent_monitorName, "parent_monitorCreateBy" : str(parent_monitorCreateBy).lower()}
    
    try: 
        if data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:configList']['b:CustomerTypeConfigMonitor'] != None:
            isNoReslut_2 = False
    except KeyError:
        pass
    
    if isNoReslut_2 == False:
        datalist_2 = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:configList']['b:CustomerTypeConfigMonitor']
    
    message = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:responseCode']
              
    if responseCode == 'Success':
        if isNoReslut_2 == False:
            if str(type(datalist_2)) == "<class 'list'>":
                for list in datalist_2:
                    custConfigId = list['b:custConfigId']
                    id = list['b:id']
                    monitorId = list['b:monitorId']
                    threshold = list['b:threshold']
                    custType = list['b:custType']
                    monitorName = list['b:monitorName']
            
                    monitormapping = {"id": str(id), "custConfigId" : str(custConfigId), "monitorId" : str(monitorId), "threshold" : str(threshold), "custType" : custType, "monitorName" : monitorName}

                    monitormapping_List.append(monitormapping)
            else:
                custConfigId = datalist_2['b:custConfigId']
                id = datalist_2['b:id']
                monitorId = datalist_2['b:monitorId']
                threshold = datalist_2['b:threshold']
                custType = datalist_2['b:custType']
                monitorName = datalist_2['b:monitorName']
            
                monitormapping = {"id": str(id), "custConfigId" : str(custConfigId), "monitorId" : str(monitorId), "threshold" : str(threshold), "custType" : custType, "monitorName" : monitorName}

                monitormapping_List.append(monitormapping)
        else:
            monitormapping = {"id": "", "custConfigId" : "", "monitorId" : "", "threshold" : "", "custType" : "", "monitorName" : ""}

            monitormapping_List.append(monitormapping)
    else:
        
        errorReason = {"message" : message}                    

        monitormapping_List.append(errorReason)
    
    return render(request, 'testdata_monitor_runs.html', {'userinfo' : userinfo, "parent_monitor" : parent_monitor, "runs" : run_List, "custTypes" : monitormapping_List})


def testdata_monitor_run_details(request, run_id):
    
    isNoReslut = True
    runDetail_List = []
    runDetail = {}
    datalist = []
    runInfo = {}

    client = Client(dmsUrl, retxml = True)

    runDetails = client.service.GetRunResultsService(run_id)

    results =  xmltodict.parse(runDetails)

    data = json.loads(json.dumps(results))

    message = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:responseCode']     
    
    run_id = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:run_id']
    
    run_name = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:run_name']
    
    monitor_id = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:monitor_id']
    
    monitor_name = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:monitor_name']
    
    runInfo = {"run_id" : run_id, "run_name" : run_name, "monitor_id" : monitor_id, "monitor_name" : monitor_name}
    
    try: 
        if data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:runDetailsList']['b:RunDetails'] != None:
            isNoReslut = False
    except KeyError:
        pass
    
    if isNoReslut == False:
        datalist = data['s:Envelope']['s:Body']['GetRunResultsServiceResponse']['GetRunResultsServiceResult']['a:runDetailsList']['b:RunDetails']
    
    if responseCode == 'Success':
        if isNoReslut == False:
            if str(type(datalist)) == "<class 'list'>":
                for list in datalist:
                    actualCreated = list['b:actualCreated']
                    custType = list['b:custType']
                    custType_id = list['b:custType_id']
                    id = list['b:id']
                    needToCreate = list['b:needToCreate']
                    run_id = list['b:run_id']
                    run_name = list['b:run_name']
            
                    runDetail = {"id": str(id), "custType" : custType, "custType_id" : str(custType_id), "run_id" : run_id, "run_name" : run_name, "needToCreate" : str(needToCreate), "actualCreated" : str(actualCreated)}

                    runDetail_List.append(runDetail)
            else:
                actualCreated = datalist['b:actualCreated']
                custType = datalist['b:custType']
                custType_id = datalist['b:custType_id']
                id = datalist['b:id']
                needToCreate = datalist['b:needToCreate']
                run_id = datalist['b:run_id']
                run_name = datalist['b:run_name']
                
            
                runDetail = {"id": str(id), "custType" : custType, "custType_id" : str(custType_id), "run_id" : run_id, "run_name" : run_name, "needToCreate" : str(needToCreate), "actualCreated" : str(actualCreated)}

                runDetail_List.append(runDetail)
        else:
            runDetail = {"id": "", "custType" : "", "custType_id" : "", "run_id" : "", "run_name" : "", "needToCreate" : "", "actualCreated" : ""}

            runDetail_List.append(runDetail)
    else:
        
        errorReason = {"message" : message}

        runDetail_List.append(errorReason)
    
    return render(request, 'testdata_monitor_run_details.html', {"run_info" : runInfo, "run_details" : runDetail_List})





def scheduleMonitor(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["monitorId"] = data['schedule_monitorId']
    request["requestBy"] = data['schedule_requestBy']
    
    request["startDate"] = datetime.strptime(data['schedule_starttime'][0:16], "%Y-%m-%dT%H:%M")
#     request["startDate"] = datetime.strptime(str(datetime.now())[0:16], "%Y-%m-%d %H:%M")
    
    scheduleMonitor = client.service.ScheduleRunService(request)

    results =  xmltodict.parse(scheduleMonitor)

    data = json.loads(json.dumps(results))
    
    id = data['s:Envelope']['s:Body']['ScheduleRunServiceResponse']['ScheduleRunServiceResult']['a:id']
    
    startDate = data['s:Envelope']['s:Body']['ScheduleRunServiceResponse']['ScheduleRunServiceResult']['a:startDate']
    
    message = data['s:Envelope']['s:Body']['ScheduleRunServiceResponse']['ScheduleRunServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['ScheduleRunServiceResponse']['ScheduleRunServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['ScheduleRunServiceResponse']['ScheduleRunServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode, "id" : str(id), "startDate" : str(startDate)}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def runMonitor(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["id"] = data['run_monitorId']
    request["requestBy"] = data['run_requestBy']
    
    runMonitor = client.service.RunMonitorService(request)

    results =  xmltodict.parse(runMonitor)

    data = json.loads(json.dumps(results))
    
#     id = data['s:Envelope']['s:Body']['RunMonitorServiceResponse']['RunMonitorServiceResult']['a:id']
    
#     startDate = data['s:Envelope']['s:Body']['RunMonitorServiceResponse']['RunMonitorServiceResult']['a:startDate']
    
    message = data['s:Envelope']['s:Body']['RunMonitorServiceResponse']['RunMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['RunMonitorServiceResponse']['RunMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['RunMonitorServiceResponse']['RunMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}   
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def testdata_monitor_config(request):
    
    isadmin = request.user.has_perm('customerFinder.configure_customer_finder')
    userinfo = {'isadmin' : isadmin}
    
    return render(request, 'testdata_monitor_config.html', {'userinfo' : userinfo})


def getProjects(request):
    
    project = {}
    project_list = []

    client = Client(cfsUrl, retxml = True)

    projects = client.service.LoadProjects()

    results =  xmltodict.parse(projects)

    data = json.loads(json.dumps(results))    

    datalist = data['s:Envelope']['s:Body']['LoadProjectsResponse']['LoadProjectsResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
    
    message = data['s:Envelope']['s:Body']['LoadProjectsResponse']['LoadProjectsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['LoadProjectsResponse']['LoadProjectsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['LoadProjectsResponse']['LoadProjectsResult']['a:responseCode']

    if responseCode == 'Success':

        for list in datalist:

            projects = list['b:KeyValueOfstringstring']

            for key,value in projects:

                id = projects[0]['b:Value']

                name = projects[1]['b:Value']

                project = {"id" : id, "name" : name}

            project_list.append(project)        
    else:

        errReason = {"message" : message}    
        
        project_list.append(errReason)

    
    if request.method == 'GET':
        
        try:
            
            HttpResponse(json.dumps(project_list), content_type='application/json')  
        
        except Exception as e:
            
            print("error as " + str(e))
             
        return HttpResponse(json.dumps(project_list), content_type='application/json')  


# def getCusttypeMapList(request):
#     
#     custtype_List = []
#     customerType = {}
# 
#     client = Client(cfsUrl, retxml = True)
# 
#     custTypes = client.service.LoadCustomerTypes("0")
# 
#     results =  xmltodict.parse(custTypes)
# 
#     data = json.loads(json.dumps(results))
# 
#     datalist = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
#     
#     message = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:message']
# 
#     errorReason = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:errorReason']
#     
#     responseCode = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:responseCode']     
# 
#     if responseCode == 'Success':
# 
#         for list in datalist:
# 
#             custTypes = list['b:KeyValueOfstringstring']            
# 
#             for key,value in custTypes:
#                 
#                 Id = custTypes[0]['b:Value']
#                 custType = custTypes[1]['b:Value']
#                 isConfigurable = custTypes[2]['b:Value']
#                 isVisible = custTypes[3]['b:Value']
#                 isEnable = custTypes[4]['b:Value']
#                 Params = custTypes[5]['b:Value']
#                 custTypeDescription = custTypes[6]['b:Value']
#                 paramDescription = custTypes[7]['b:Value']            
# 
#                 customerType = {"Id": Id, "custType" : custType, "isConfigurable" : isConfigurable, "isVisible" : isVisible, "isEnable" : isEnable, "Params" : Params, "custTypeDescription" : custTypeDescription , "paramDescription" : paramDescription}
# 
#             custtype_List.append(customerType)
# 
#     else:
#         
#         errorReason = {"message" : message}                    
# 
#         custtype_List.append(errorReason)
# 
#     if request.method == 'GET':                                        
#     
#         return HttpResponse(json.dumps(custtype_List), content_type='application/json')  


def getActions(request):
    
    action_List = []
    action = {}

    client = Client(dmsUrl, retxml = True)
    
    actions = client.service.GetExistingAPIs()
    
    results =  xmltodict.parse(actions)
    
    data = json.loads(json.dumps(results))
    
    datalist = data['s:Envelope']['s:Body']['GetExistingAPIsResponse']['GetExistingAPIsResult']['a:actionList']['b:string']
    
    message = data['s:Envelope']['s:Body']['GetExistingAPIsResponse']['GetExistingAPIsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetExistingAPIsResponse']['GetExistingAPIsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetExistingAPIsResponse']['GetExistingAPIsResult']['a:responseCode']     

    if responseCode == 'Success':

        for list in datalist:
            
            action = {"name": list}

            action_List.append(action)

    else:
        
        errorReason = {"message" : message}                    

        action_List.append(errorReason)

    if request.method == 'GET':                                        
    
        return HttpResponse(json.dumps(action_List), content_type='application/json')
    

def loadCustTypes(request):
    
    custtype_List = []
    customerType = {}

    client = Client(dmsUrl, retxml = True)
    
    custTypes = client.service.GetExistingCustomerTypeConfigs()
    
    results =  xmltodict.parse(custTypes)
    
    data = json.loads(json.dumps(results))
    
    datalist = data['s:Envelope']['s:Body']['GetExistingCustomerTypeConfigsResponse']['GetExistingCustomerTypeConfigsResult']['a:custTypeList']['b:CustomerTypeConfig']
    
    message = data['s:Envelope']['s:Body']['GetExistingCustomerTypeConfigsResponse']['GetExistingCustomerTypeConfigsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetExistingCustomerTypeConfigsResponse']['GetExistingCustomerTypeConfigsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetExistingCustomerTypeConfigsResponse']['GetExistingCustomerTypeConfigsResult']['a:responseCode']     

    if responseCode == 'Success':

        for list in datalist:
            
            id = list['b:id']
            custType = list['b:custType']
            desc = list['b:desc']
            realCustType = list['b:realCustType']
            
            customerType = {"id": str(id), "name" : custType, "desc" : desc, "realCustType" : realCustType}

            custtype_List.append(customerType)

    else:
        
        errorReason = {"message" : message}                    

        custtype_List.append(errorReason)

    if request.method == 'GET':                                        
    
        return HttpResponse(json.dumps(custtype_List), content_type='application/json')
    

def loadMonitors(request):
    
    monitor_List = []
    monitor = {}

    client = Client(dmsUrl, retxml = True)

    monitors = client.service.GetExsitingMonitors()

    results =  xmltodict.parse(monitors)

    data = json.loads(json.dumps(results))

    datalist = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:monitorList']['b:Monitor']
    
    message = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetExsitingMonitorsResponse']['GetExsitingMonitorsResult']['a:responseCode']     

    if responseCode == 'Success':

        for list in datalist:
            id = list['b:id']
            name = list['b:name']
            description = list['b:description']
            appendQueryClause = list['b:appendQueryClause']
            createBy = list['b:createBy']
            emailPrefix = list['b:emailPrefix']
            environmentId = list['b:environmentId']
            environmentName = list['b:environmentName']
            intervalDays = list['b:intervalDays']
            isIPS = list['b:isIPS']
            multipleLayer = list['b:multipleLayer']
            productCode = list['b:productCode']
            projectId = list['b:projectID']
            projectName = list['b:projectName']
            scheduledStartTime = list['b:scheduledStartTime']
            userIDPrefix = list['b:userIDPrefix']
            
            monitor = {"id": str(id), "name" : name, "description" : description, "appendQueryClause" : appendQueryClause, "createBy" : createBy,
                       "emailPrefix" : emailPrefix, "environmentId" : str(environmentId), "environmentName" : environmentName, "intervalDays" : intervalDays, "isIPS" : str(isIPS), "multipleLayer" : str(multipleLayer), "productCode" : str(productCode),
                       "projectId" : str(projectId), "projectName" : projectName, "scheduledStartTime" : str(scheduledStartTime), "userIDPrefix" :userIDPrefix}

            monitor_List.append(monitor)

    else:
        
        errorReason = {"message" : message}                    

        monitor_List.append(errorReason)

    if request.method == 'GET':                                        
    
        return HttpResponse(json.dumps(monitor_List), content_type='application/json')  

def addChain(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["action"] = data['new_chain_action']
    request["delay"] = data['new_chain_delay']
    request["id"] = 0
    request["original"] = data['new_chain_original']
    request["target"] = data['new_chain_target']
    
    addCustType = client.service.AddCustomerTypeChainService(request)

    results =  xmltodict.parse(addCustType)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['AddCustomerTypeChainServiceResponse']['AddCustomerTypeChainServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['AddCustomerTypeChainServiceResponse']['AddCustomerTypeChainServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['AddCustomerTypeChainServiceResponse']['AddCustomerTypeChainServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def updateChain(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["action"] = data['update_chain_action']
    request["delay"] = data['update_chain_delay']
    request["id"] = data['update_chain_id']
    request["original"] = data['update_chain_original_custtype']
    request["target"] = data['update_chain_target_custtype']

    updateChain = client.service.UpdateCustomerTypeChainService(request)

    results =  xmltodict.parse(updateChain)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['UpdateCustomerTypeChainServiceResponse']['UpdateCustomerTypeChainServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['UpdateCustomerTypeChainServiceResponse']['UpdateCustomerTypeChainServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['UpdateCustomerTypeChainServiceResponse']['UpdateCustomerTypeChainServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')
  

def addCustType(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["custType"] = data['new_custtype_name']
    request["desc"] = data['new_custtype_desc']
    request["id"] = 0
    request["realCustType"] = data['new_custtype_real']
    
    addCustType = client.service.AddCustomerTypeService(request)

    results =  xmltodict.parse(addCustType)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['AddCustomerTypeServiceResponse']['AddCustomerTypeServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['AddCustomerTypeServiceResponse']['AddCustomerTypeServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['AddCustomerTypeServiceResponse']['AddCustomerTypeServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def updateCustType(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["custType"] = data['update_custtype_name']
    request["desc"] = data['update_custtype_desc']
    request["id"] = data['update_custtype_id']
    request["realCustType"] = data['update_custtype_real']

    updateCustType = client.service.UpdateCustomerTypeService(request)

    results =  xmltodict.parse(updateCustType)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['UpdateCustomerTypeServiceResponse']['UpdateCustomerTypeServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['UpdateCustomerTypeServiceResponse']['UpdateCustomerTypeServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['UpdateCustomerTypeServiceResponse']['UpdateCustomerTypeServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def deleteCustType(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)

    deleteCustType = client.service.DeleteCustomerTypeService(data['delete_custtype_id'])

    results =  xmltodict.parse(deleteCustType)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['DeleteCustomerTypeServiceResponse']['DeleteCustomerTypeServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['DeleteCustomerTypeServiceResponse']['DeleteCustomerTypeServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['DeleteCustomerTypeServiceResponse']['DeleteCustomerTypeServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def addMonitor(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["appendQeuryClause"] = data['new_monitor_append_query']
    request["createBy"] = data['new_monitor_create_by']
    request["desc"] = data['new_monitor_desc']
    request["emailPrefix"] = data['new_monitor_email']
    
    request["envId"] = data['new_monitor_env_id']
    request["id"] = 0
    request["intervalDays"] = data['new_monitor_interval_days']
    request["isIPS"] = data['new_monitor_ips']
    
    request["multipleLayer"] = data['new_monitor_multiple_layer']
    request["name"] = data['new_monitor_name']
    request["productCode"] = data['new_monitor_product_code']
    request["projectId"] = data['new_monitor_project_id']
    
    request["scheduleStartTime"] = datetime.strptime(data['new_monitor_scheduled_starttime'][0:16], "%Y-%m-%dT%H:%M")
    request["userIDPrefix"] = data['new_monitor_user_id']
    

    addMonitor = client.service.AddMonitorService(request)

    results =  xmltodict.parse(addMonitor)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['AddMonitorServiceResponse']['AddMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['AddMonitorServiceResponse']['AddMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['AddMonitorServiceResponse']['AddMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def updateMonitor(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["appendQeuryClause"] = data['update_monitor_append_query']
    
    request["createBy"] = data['update_monitor_create_by']
    request["desc"] = data['update_monitor_desc']
    request["emailPrefix"] = data['update_monitor_email']
    
    request["envId"] = data['update_monitor_env_id']
    request["id"] = data['update_monitor_id']
    request["intervalDays"] = data['update_monitor_interval_days']
    request["isIPS"] = data['update_monitor_ips']
    
    request["multipleLayer"] = data['update_monitor_multiple_layer']
    request["name"] = data['update_monitor_name']
    request["productCode"] = data['update_monitor_product_code']
    request["projectId"] = data['update_monitor_project_id']
    
    request["scheduleStartTime"] = datetime.strptime(data['update_monitor_scheduled_starttime'][0:16], "%Y-%m-%dT%H:%M")
    request["userIDPrefix"] = data['update_monitor_user_id']
    
    updateMonitor = client.service.UpdateMonitorService(request)

    results =  xmltodict.parse(updateMonitor)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['UpdateMonitorServiceResponse']['UpdateMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['UpdateMonitorServiceResponse']['UpdateMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['UpdateMonitorServiceResponse']['UpdateMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')

def deleteMonitor(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)

    deleteMonitor = client.service.DeleteMonitorService(data['delete_monitor_id'])

    results =  xmltodict.parse(deleteMonitor)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['DeleteMonitorServiceResponse']['DeleteMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['DeleteMonitorServiceResponse']['DeleteMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['DeleteMonitorServiceResponse']['DeleteMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def loadMappings(request):
    
    isNoReslut = True
    monitormapping_List = []
    monitormapping = {}
    datalist = []
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    getMonitorDetails = client.service.GetMonitorDetails(data["selected_monitor_id"])

    results =  xmltodict.parse(getMonitorDetails)

    data = json.loads(json.dumps(results))
    
    try: 
        if data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:configList']['b:CustomerTypeConfigMonitor'] != None:
            isNoReslut = False
    except KeyError:
        pass
    
    if isNoReslut == False:
        datalist = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:configList']['b:CustomerTypeConfigMonitor']
    
    message = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetMonitorDetailsResponse']['GetMonitorDetailsResult']['a:responseCode']
              
    if responseCode == 'Success':
        if isNoReslut == False:
            if str(type(datalist)) == "<class 'list'>":
                for list in datalist:
                    custConfigId = list['b:custConfigId']
                    id = list['b:id']
                    monitorId = list['b:monitorId']
                    threshold = list['b:threshold']
                    custType = list['b:custType']
                    monitorName = list['b:monitorName']
            
                    monitormapping = {"id": str(id), "custConfigId" : str(custConfigId), "monitorId" : str(monitorId), "threshold" : str(threshold), "custType" : custType, "monitorName" : monitorName}

                    monitormapping_List.append(monitormapping)
            else:
                custConfigId = datalist['b:custConfigId']
                id = datalist['b:id']
                monitorId = datalist['b:monitorId']
                threshold = datalist['b:threshold']
                custType = datalist['b:custType']
                monitorName = datalist['b:monitorName']
            
                monitormapping = {"id": str(id), "custConfigId" : str(custConfigId), "monitorId" : str(monitorId), "threshold" : str(threshold), "custType" : custType, "monitorName" : monitorName}

                monitormapping_List.append(monitormapping)
        else:
            monitormapping = {"id": "", "custConfigId" : "", "monitorId" : "", "threshold" : "", "custType" : "", "monitorName" : ""}

            monitormapping_List.append(monitormapping)
    else:
        
        errorReason = {"message" : message}                    

        monitormapping_List.append(errorReason)

    return HttpResponse(json.dumps(monitormapping_List), content_type='application/json')  


def addMapping(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["configId"] = data['new_mapping_configid']
    request["id"] = 0
    request["monitorId"] = data['new_mapping_monitorid']
    request["threshold"] = data['new_mapping_threshold']
    

    addMapping = client.service.AddCustomerTypeConfigMonitorService(request)

    results =  xmltodict.parse(addMapping)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['AddCustomerTypeConfigMonitorServiceResponse']['AddCustomerTypeConfigMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['AddCustomerTypeConfigMonitorServiceResponse']['AddCustomerTypeConfigMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['AddCustomerTypeConfigMonitorServiceResponse']['AddCustomerTypeConfigMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def updateMapping(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)
    
    request = {}                
         
    request["configId"] = data['update_mapping_custtype']
    request["id"] = data['update_mapping_id']
    request["monitorId"] = data['update_mapping_monitor']
    request["threshold"] = data['update_mapping_threshold']
    
    updateMapping = client.service.UpdateCustomerTypeFromMonitorService(request)

    results =  xmltodict.parse(updateMapping)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['UpdateCustomerTypeFromMonitorServiceResponse']['UpdateCustomerTypeFromMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['UpdateCustomerTypeFromMonitorServiceResponse']['UpdateCustomerTypeFromMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['UpdateCustomerTypeFromMonitorServiceResponse']['UpdateCustomerTypeFromMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def deleteMapping(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)

    deleteMapping = client.service.DeleteCustomerTypeConfigMonitorService(data['delete_mapping_id'])

    results =  xmltodict.parse(deleteMapping)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['DeleteCustomerTypeConfigMonitorServiceResponse']['DeleteCustomerTypeConfigMonitorServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['DeleteCustomerTypeConfigMonitorServiceResponse']['DeleteCustomerTypeConfigMonitorServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['DeleteCustomerTypeConfigMonitorServiceResponse']['DeleteCustomerTypeConfigMonitorServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')


def loadChains(request):
    
    chain_List = []
    chain = {}

    client = Client(dmsUrl, retxml = True)

    chains = client.service.GetExistingCustomerTypeAndActionsService()

    results =  xmltodict.parse(chains)

    data = json.loads(json.dumps(results))

    datalist = data['s:Envelope']['s:Body']['GetExistingCustomerTypeAndActionsServiceResponse']['GetExistingCustomerTypeAndActionsServiceResult']['a:nodes']['b:CustTypeAndActionNode']
    
    message = data['s:Envelope']['s:Body']['GetExistingCustomerTypeAndActionsServiceResponse']['GetExistingCustomerTypeAndActionsServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetExistingCustomerTypeAndActionsServiceResponse']['GetExistingCustomerTypeAndActionsServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetExistingCustomerTypeAndActionsServiceResponse']['GetExistingCustomerTypeAndActionsServiceResult']['a:responseCode']     

    if responseCode == 'Success':

        for list in datalist:
            id = list['b:id']
            action = list['b:action']
            delay = list['b:delay']
            originalCustTypeId = list['b:originalCustTypeId']
            targetCustTypeId = list['b:targetCustTypeId']
            originalCustType = list['b:originalCustType']
            targetCustType = list['b:targetCustType']
            
            chain = {"id": str(id), "action" : action, "delay" : delay, "originalCustTypeId" : originalCustTypeId, "targetCustTypeId" : targetCustTypeId, "originalCustType" : originalCustType, "targetCustType" : targetCustType}

            chain_List.append(chain)

    else:
        
        errorReason = {"message" : errorReason}                    

        chain_List.append(errorReason)

    if request.method == 'GET':                                        
    
        return HttpResponse(json.dumps(chain_List), content_type='application/json')  


def deleteChain(request):
    
    data = json.loads(request.POST.get('myjsondata'))
   
    client = Client(dmsUrl, retxml = True)

    deleteChain = client.service.DeleteCustomerTypeChainService(data['delete_chain_id'])

    results =  xmltodict.parse(deleteChain)

    data = json.loads(json.dumps(results))
    
    message = data['s:Envelope']['s:Body']['DeleteCustomerTypeChainServiceResponse']['DeleteCustomerTypeChainServiceResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['DeleteCustomerTypeChainServiceResponse']['DeleteCustomerTypeChainServiceResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['DeleteCustomerTypeChainServiceResponse']['DeleteCustomerTypeChainServiceResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"message" : message, "responseCode": responseCode}

    else:

        values = {"message" : message}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')








