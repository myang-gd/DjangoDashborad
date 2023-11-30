#auth/views.py

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.backends import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render
import requests
import xmltodict
import json,datetime
#from apps.customerFinder.logger import Logger
from django import forms
from suds.client import Client
#from apps.card_finder.models import Product
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from _overlapped import NULL

#Initialize Global Variables
url = 'http://gdcqatools01:82/CustomerFinderService/CustomerFinderService.svc?wsdl'

#url = 'http://10.50.14.112/test/CustomerFinderService.svc?wsdl' 
    
def customerFinder(request):    

    value = None
    jsonArray = None
    error = None
    product_list = None
    type = None                         
                
    return render(request, 'customerFinder.html')

#Provide an interface to get environment code such as: QA3, QA4, QA5, Production
def getEnvironment(request):
    
    environment = ['QA3','QA4','QA5','Production']
    
    if request.method == 'GET':
    
        return HttpResponse(json.dumps(environment), content_type='application/json')
         
    
def getProjects(request):
    
    datalist = []
    projects = []
    project_list = []
    proj = {}

    client = Client(url,retxml = True)

    #Call Fucntion
    projects = client.service.LoadProjects()

    #Convert xml to dict
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

                projectId = int(projects[0]['b:Value'])

                projectName = projects[1]['b:Value']

                proj = {"Id":projectId, "projectName":projectName}

            project_list.append(proj)            
    else:

        errReason = {"errorReason":errorReason}    
        
        project_list.append(errReason)

    
    if request.method == 'GET':
        
        try:
            
            HttpResponse(json.dumps(project_list), content_type='application/json')  
        
        except Exception as e:
            
            print("error as " + str(e))
             
        return HttpResponse(json.dumps(project_list), content_type='application/json')            
    
def getCusttypeMapList(request):
    
    if 'project' in request.GET:
        project = request.GET.get('project')
    
    if 'data_Base_Id' in request.GET:
        database = request.GET.get('data_Base_Id')
    
    datalist = []
    custTypes = []
    custtype_List = []
    customerType = {}

    client = Client(url,retxml = True)

    #Call Fucntion
    custTypes = client.service.LoadCustomerTypes(projectName=str(project), dataBaseId=str(database))

    #Convert xml to dict
    results =  xmltodict.parse(custTypes)

    data = json.loads(json.dumps(results))

    datalist = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
    
    message = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:responseCode']     

    if responseCode == 'Success':

        for list in datalist:

            custTypes = list['b:KeyValueOfstringstring']            

            for key,value in custTypes:
                
                Id = custTypes[0]['b:Value']
                custType = custTypes[1]['b:Value']
                isConfigurable = custTypes[2]['b:Value']
                isVisible = custTypes[3]['b:Value']
                isEnable = custTypes[4]['b:Value']
                Params = custTypes[5]['b:Value']
                custTypeDescription = custTypes[6]['b:Value']
                paramDescription = custTypes[7]['b:Value']            

                customerType = {"Id": Id, "custType" : custType, "isConfigurable" : isConfigurable, "isVisible" : isVisible, "isEnable" : isEnable, "Params" : Params, "custTypeDescription" : custTypeDescription, "paramDescription" : paramDescription}

            custtype_List.append(customerType)

    else:
        
        errorReason = {"errorReason":errorReason}                    

        custtype_List.append(errorReason)

    if request.method == 'GET':                                        
    
        return HttpResponse(json.dumps(custtype_List), content_type='application/json')  
    

def getProductMap(request):        
    
    if 'project' in request.GET:
        project = request.GET.get('project')
    
    if 'data_Base_Id' in request.GET:
        database = request.GET.get('data_Base_Id')
    
    datalist = []
    productMap = []
    product_List = []

    client = Client(url,retxml = True)

    #Call Fucntion
    productMap = client.service.LoadProductMaps(projectName=str(project), dataBaseId=str(database))

    #Convert xml to dict
    results =  xmltodict.parse(productMap)

    data = json.loads(json.dumps(results))
    
    if str(database) == '1':
        datalist = data['s:Envelope']['s:Body']['LoadProductMapsResponse']['LoadProductMapsResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
    
        message = data['s:Envelope']['s:Body']['LoadProductMapsResponse']['LoadProductMapsResult']['a:message']

        errorReason = data['s:Envelope']['s:Body']['LoadProductMapsResponse']['LoadProductMapsResult']['a:errorReason']
    
        responseCode = data['s:Envelope']['s:Body']['LoadProductMapsResponse']['LoadProductMapsResult']['a:responseCode']     

        if responseCode == 'Success':

            for list in datalist:

                productMap = list['b:KeyValueOfstringstring']

                for key,value in productMap:

                    Id = productMap[0]['b:Value'] 
                    productType = productMap[1]['b:Value']
                    productKey = productMap[2]['b:Value']
                    ipsProductKey = productMap[3]['b:Value']
                    isEnable = productMap[4]['b:Value']
                    projectName = productMap[5]['b:Value']
                                                                       

                    productkey = {"Id" : Id, "productType" : productType, "productKey" : productKey, "ipsProductKey": ipsProductKey, "isEnable" : isEnable, "projectName" : projectName}

                product_List.append(productkey)      
    
        else: 

            errorReason = {"errorReason":errorReason}      

            product_List.append(errorReason)


    if request.method == 'GET':
    
        return HttpResponse(json.dumps(product_List), content_type='application/json')        
                
    return productMap          


def getQuery(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        database = data["database"]
        env = data["env"]               
        products = data["products"]
        custtypes = data["selected_custtypes"]                
        email = data["email"]
        appendExtendQuery = data["extendedquery"]
        project = data["project"]
        isips = data["isips"]    

    client = Client(url,retxml = True)

    #Call Fucntion
    getquery = client.service.GetQuery(env = env, product = products, customerType = custtypes, email = email, appendExtendQuery = appendExtendQuery, projectName = str(project), dataBaseId = str(database), isips = isips)

    #Convert xml to dict
    results =  xmltodict.parse(getquery)

    data = json.loads(json.dumps(results))

    sqlQuery = data['s:Envelope']['s:Body']['GetQueryResponse']['GetQueryResult']['a:result']
    
    message = data['s:Envelope']['s:Body']['GetQueryResponse']['GetQueryResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['GetQueryResponse']['GetQueryResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['GetQueryResponse']['GetQueryResult']['a:responseCode']

    if responseCode == 'Success':                     
                
        Sql = {"sqlQuery" : sqlQuery, "message": message, "responseCode" : responseCode}      

    else:
        
        Sql = {"errorReason":errorReason}                      
            
    return HttpResponse(json.dumps(Sql), content_type='application/json')   


def loadQuerysByCustType(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))                
             
        custtype = data["customerTypeName"]
        database = data["databaseId"]               
        
    datalist = []    
    subQueries = []
    subquery_List = []
    subQueryInfo = {}
        
        
    client = Client(url,retxml = True)

    #Call Fucntion
    getquery = client.service.LoadQuerys(customerType = custtype, dataBaseId = str(database))

    #Convert xml to dict
    results =  xmltodict.parse(getquery)

    data = json.loads(json.dumps(results))                       
    
    message = data['s:Envelope']['s:Body']['LoadQuerysResponse']['LoadQuerysResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['LoadQuerysResponse']['LoadQuerysResult']['a:errorReason']
	
    responseCode = data['s:Envelope']['s:Body']['LoadQuerysResponse']['LoadQuerysResult']['a:responseCode']

    if responseCode == 'Success':
        
        sqlQuery = data['s:Envelope']['s:Body']['LoadQuerysResponse']['LoadQuerysResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
    	
        if str(type(sqlQuery)) == "<class 'dict'>":
            
            datalist.append(sqlQuery)  
            
        else:
            
            datalist = sqlQuery        
        
        for list in datalist:

            subQueries = list['b:KeyValueOfstringstring']

            for key,value in subQueries:
                    
                Id = subQueries[0]['b:Value'] 

                SQLCommand = subQueries[1]['b:Value']
            
                SelectListItem = subQueries[2]['b:Value']
            
                TableListItem = subQueries[3]['b:Value']
                
                Alias = subQueries[4]['b:Value']
                
                JoinCondition = subQueries[5]['b:Value']
                
                FilterCondition = subQueries[6]['b:Value']
                
                FilterParam = subQueries[7]['b:Value']
                
                SelfDefinedSQLQuery = subQueries[8]['b:Value']
                
                CustomerTypeName = subQueries[9]['b:Value']            
                
                IsEnable = subQueries[10]['b:Value']
                
                ProjectName = subQueries[11]['b:Value']
                
                CommandSequence = subQueries[12]['b:Value']
                
                SubSequence = subQueries[13]['b:Value']

                CutomerTypeId = subQueries[14]['b:Value']

                JoinSequence = subQueries[15]['b:Value']
              
                subQueryInfo = {"Id" : Id, "SQLCommand" : SQLCommand, "SelectListItem" : SelectListItem, "TableListItem" : TableListItem, "Alias" : Alias, "JoinCondition" : JoinCondition, "FilterCondition" : FilterCondition, "FilterParam" : FilterParam, "SelfDefinedSQLQuery" : SelfDefinedSQLQuery, "CustomerTypeName" : CustomerTypeName, "IsEnable" : IsEnable, "ProjectName" : ProjectName, "CommandSequence" : CommandSequence, "SubSequence" : SubSequence, "CutomerTypeId" : CutomerTypeId, "JoinSequence" : JoinSequence}                       
                    
            subquery_List.append(subQueryInfo)     

    else:			
		
        errorReason = {"errorReason":errorReason}
                                   
        subquery_List.append(errorReason)                           
      
    return HttpResponse(json.dumps(subquery_List), content_type='application/json')   

    
def getCustomer(request):
    
    #customer = {'customerkey':'8522074'}                                                
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        database = data["database"]
        env = data["env"]
        products = data["products"]
        custtypes = data["selected_custtypes"]                
        email = data["email"]
        appendExtendQuery = data["extendedquery"]
        project = data["project"]
        isips = data["isips"]    
        isCheckPassword = data["isCheckPassword"]

    client = Client(url,retxml = True)

    #Call Fucntion
    findcustomer = client.service.FindCustomer(env = env, product = products, customerType = custtypes, email = email, appendExtendQuery = appendExtendQuery, projectName = str(project), dataBaseId = str(database), isips = isips, ischeckpwd = isCheckPassword)

    #Convert xml to dict
    results =  xmltodict.parse(findcustomer)

    data = json.loads(json.dumps(results))

    customer = data['s:Envelope']['s:Body']['FindCustomerResponse']['FindCustomerResult']['a:result']        
    
    #Output success message or error message
    message = data['s:Envelope']['s:Body']['FindCustomerResponse']['FindCustomerResult']['a:message']

    #Output fail reasons
    errorReason = data['s:Envelope']['s:Body']['FindCustomerResponse']['FindCustomerResult']['a:errorReason']
    
    #Success or Failed
    responseCode = data['s:Envelope']['s:Body']['FindCustomerResponse']['FindCustomerResult']['a:responseCode']  

    if responseCode == 'Success':
             
        customerKey = customer['b:customerKey']
        
        accountIdentifier = customer['b:accountIdentifier']
        
        consumerProfileKey = customer['b:consumerProfileKey']
        
        userId = customer['b:userId']
        
        email = customer['b:email']
        
        sqlQuery = customer['b:sqlQuery']            
                
        values = {"customerKey" : customerKey, "accountIdentifier" : accountIdentifier, "consumerProfileKey" : consumerProfileKey, "userId": userId, "email": email, "sqlQuery" : sqlQuery, "message" : message, "responseCode" : responseCode}      

    else:

        values = {"errorReason": errorReason}
            
    return HttpResponse(json.dumps(values), content_type='application/json')       
       

def getEmailPrefix(request):
    
    if 'project' in request.GET:
        project = request.GET.get('project')
    
    if 'data_Base_Id' in request.GET:
        database = request.GET.get('data_Base_Id')
    
    datalist = []
    emailprefixes = []    
    emailprefix_List = []
    emailprefixinfo = {}       
    prefixes = []    

    client = Client(url,retxml = True)

    #Call Fucntion
    emailprefix = client.service.LoadEmailPrefixes(projectName = str(project), dataBaseId = str(database))

    #Convert xml to dict
    results =  xmltodict.parse(emailprefix)
    
    data = json.loads(json.dumps(results))    
    
    if str(database) == '1':
    #Success or Failed
        responseCode = data['s:Envelope']['s:Body']['LoadEmailPrefixesResponse']['LoadEmailPrefixesResult']['a:responseCode'] 

        prefixes = data['s:Envelope']['s:Body']['LoadEmailPrefixesResponse']['LoadEmailPrefixesResult']['a:result']['b:ArrayOfKeyValueOfstringstring']           
    
    #Output success message
        message = data['s:Envelope']['s:Body']['LoadEmailPrefixesResponse']['LoadEmailPrefixesResult']['a:message']

    #Output fail reasons
        errorReason = data['s:Envelope']['s:Body']['LoadEmailPrefixesResponse']['LoadEmailPrefixesResult']['a:errorReason']    

        if responseCode == 'Success':                                

            if str(type(prefixes)) == "<class 'dict'>":
            
                datalist.append(prefixes)  
            
            else:
            
                datalist = prefixes        
        
            for list in datalist:

                emailprefixes = list['b:KeyValueOfstringstring']

                for key,value in emailprefixes:
                    
                    Id = emailprefixes[0]['b:Value'] 

                    Name = emailprefixes[1]['b:Value']
            
                    IsEnable = emailprefixes[2]['b:Value']
            
                    ProjectName = emailprefixes[3]['b:Value']
        
                    emailprefixinfo = {"Id" : Id, "Name" : Name, "IsEnable" : IsEnable, "ProjectName" : ProjectName}
                
                emailprefix_List.append(emailprefixinfo)    

        else:
            errorReason = {"errorReason": errorReason}       

            emailprefix_List.append(errorReason)

    if request.method == 'GET':            
            
        return HttpResponse(json.dumps(emailprefix_List), content_type='application/json')    

def getUserIDPrefix(request):
    
    if 'project' in request.GET:
        project = request.GET.get('project')
    
    if 'data_Base_Id' in request.GET:
        database = request.GET.get('data_Base_Id')
    
    datalist = []
    useridprefixes = []
    useridprefix_List = []
    useridprefixinfo = {}   
    prefixes = []   

    client = Client(url,retxml = True)

    #Call Fucntion
    useridprefix = client.service.LoadUserIDPrefixes(projectName = str(project), dataBaseId = str(database))

    #Convert xml to dict
    results =  xmltodict.parse(useridprefix)

    data = json.loads(json.dumps(results))
    
    if str(database) == '1':
    #Success or Failed
        responseCode = data['s:Envelope']['s:Body']['LoadUserIDPrefixesResponse']['LoadUserIDPrefixesResult']['a:responseCode']                              

        prefixes = data['s:Envelope']['s:Body']['LoadUserIDPrefixesResponse']['LoadUserIDPrefixesResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
    
    #Output success message or error message
        message = data['s:Envelope']['s:Body']['LoadUserIDPrefixesResponse']['LoadUserIDPrefixesResult']['a:message']

    #Output fail reasons
        errorReason = data['s:Envelope']['s:Body']['LoadUserIDPrefixesResponse']['LoadUserIDPrefixesResult']['a:errorReason']

        if responseCode == 'Success':
    
            if str(type(prefixes)) == "<class 'dict'>":
            
                datalist.append(prefixes)  
            
            else:
            
                datalist = prefixes     
                 
            for list in datalist:

                useridprefixes = list['b:KeyValueOfstringstring']        

                for key,value in useridprefixes:

                    Id = useridprefixes[0]['b:Value']
        
                    Name = useridprefixes[1]['b:Value']
                
                    IsEnable = useridprefixes[2]['b:Value']
                
                    ProjectName = useridprefixes[3]['b:Value']
        
                    useridprefixinfo = {"Id" : Id, "Name" : Name, "IsEnable" : IsEnable, "ProjectName" : ProjectName}                                       
         
                useridprefix_List.append(useridprefixinfo)      

        else:

            errorReason = {"errorReason": errorReason}

            useridprefix_List.append(errorReason)              

    if request.method == 'GET':            
            
        return HttpResponse(json.dumps(useridprefix_List), content_type='application/json')

def getPasswordRule(request):    

    if 'project' in request.GET:
        project = request.GET.get('project')
        
    if 'data_Base_Id' in request.GET:
        database = request.GET.get('data_Base_Id')
           
    datalist = []
    passwordrules = []
    passwordrule_List = []
    passwordruleinfo = {}   
    rules = []   

    client = Client(url,retxml = True)

    #Call Fucntion
    passwordrule = client.service.LoadPasswordRules(projectName = str(project), dataBaseId = str(database))

    #Convert xml to dict
    results =  xmltodict.parse(passwordrule)

    data = json.loads(json.dumps(results))       
    
    if str(database) == '1':
    #Success or Failed
        responseCode = data['s:Envelope']['s:Body']['LoadPasswordRulesResponse']['LoadPasswordRulesResult']['a:responseCode']                              

        rules = data['s:Envelope']['s:Body']['LoadPasswordRulesResponse']['LoadPasswordRulesResult']['a:result']['b:ArrayOfKeyValueOfstringstring']
    
    #Output success message or error message
        message = data['s:Envelope']['s:Body']['LoadPasswordRulesResponse']['LoadPasswordRulesResult']['a:message']

    #Output fail reasons
        errorReason = data['s:Envelope']['s:Body']['LoadPasswordRulesResponse']['LoadPasswordRulesResult']['a:errorReason']

        if responseCode == 'Success':
    
            if str(type(rules)) == "<class 'dict'>":
            
                datalist.append(rules)  
            
            else:
            
                datalist = rules     
                 
            for list in datalist:

                passwordrules = list['b:KeyValueOfstringstring']        

                for key,value in passwordrules:

                    Id = passwordrules[0]['b:Value']
        
                    UserIdRegex = passwordrules[1]['b:Value']
                
                    UserPassword = passwordrules[2]['b:Value']

                    IsEnable = passwordrules[3]['b:Value']
                
                    ProjectName = passwordrules[4]['b:Value']
        
                    passwordruleinfo = {"Id" : Id, "UserIdRegex" : UserIdRegex, "UserPassword" : UserPassword, "IsEnable" : IsEnable, "ProjectName" : ProjectName}                                       
         
                passwordrule_List.append(passwordruleinfo)      

        else:

            errorReason = {"errorReason": errorReason}

            passwordrule_List.append(errorReason)              

    if request.method == 'GET':            
            
        return HttpResponse(json.dumps(passwordrule_List), content_type='application/json')
    
def customerFinderConfig(request):
     
    value = None
    jsonArray = None
    error = None
    product_list = None
    type = None
#     isadmin = request.user.is_superuser
    isadmin = request.user.has_perm('customerFinder.configure_customer_finder')
    userinfo = {'isadmin' : isadmin}
    
    return render(request, 'customerFinder_config.html', {'userinfo' : userinfo})

def addCustType(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                 
        
        rData["changeBy"] = request.user.username
        if str(data["isConfigurable"]) == "True":
           rData["isConfigurable"] = True
        else:
           rData["isConfigurable"] = False
        
        if str(data["isVisible"]) == "True":
           rData["isVisible"] = True
        else:
           rData["isVisible"] = False
                                                   
        rData["id"] = ''       
        rData["dataBaseId"] = data["dataBaseId"] 
        rData["name"] = data["customerTypeName"]
        rData["typeDescription"] = data["customerTypeDesc"]
        rData["param"] = data["params"]
        rData["paramDescription"] = data["paramsDesc"]
        rData["projectName"] = data["projectName"] 
   
    client = Client(url,retxml = True)

    #Call Fucntion
    addCustType = client.service.AddCustomerType(rData)

    #Convert xml to dict
    results =  xmltodict.parse(addCustType)

    data = json.loads(json.dumps(results))
    
    result = data['s:Envelope']['s:Body']['AddCustomerTypeResponse']['AddCustomerTypeResult']['a:result']
    
    message = data['s:Envelope']['s:Body']['AddCustomerTypeResponse']['AddCustomerTypeResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['AddCustomerTypeResponse']['AddCustomerTypeResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['AddCustomerTypeResponse']['AddCustomerTypeResult']['a:responseCode']
                 
    if responseCode == 'Success':

        values = {"result": result, "message" : message, "responseCode": responseCode}  

    else:

        values = {"errorReason": errorReason}       
        
    return HttpResponse(json.dumps(values), content_type='application/json')

def updateCustType(request):
    
    rData = {}
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
                
        rData["changeBy"] = "wchen"
        if str(data["isConfigurable"]) == "True":
           rData["isConfigurable"] = True
        else:
           rData["isConfigurable"] = False
        
        if str(data["isVisible"]) == "True":
           rData["isVisible"] = True
        else:
           rData["isVisible"] = False  
                         
        rData["id"] = int(data["customerTypeId"])
        rData["name"] = data["customerTypeName"]
        rData["typeDescription"] = data["customerTypeDesc"]
        rData["param"] = data["params"]
        rData["paramDescription"] = data["paramsDesc"]
        rData["projectName"] = data["projectName"]       
           
    client = Client(url,retxml = True)

    #Call Fucntion
    print("rdata as:" + str(rData))
    updateCustType = client.service.UpdateCustomerType(rData)

    #Convert xml to dict
    results =  xmltodict.parse(updateCustType)

    data = json.loads(json.dumps(results))
              
    #data['s:Envelope']['s:Body']['UpdateCustomerTypeResponse']['UpdateCustomerTypeResult']
    
    result = data['s:Envelope']['s:Body']['UpdateCustomerTypeResponse']['UpdateCustomerTypeResult']['a:result']
    
    message = data['s:Envelope']['s:Body']['UpdateCustomerTypeResponse']['UpdateCustomerTypeResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['UpdateCustomerTypeResponse']['UpdateCustomerTypeResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['UpdateCustomerTypeResponse']['UpdateCustomerTypeResult']['a:responseCode']
    
    if responseCode == 'Success':          
        
        values = {"result": result, "message" : message, "responseCode": responseCode}  

    else:

        values = {"errorReason": errorReason}
    
    return HttpResponse(json.dumps(values), content_type='application/json')

def enableDisableCustType(request):    
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["changeBy"] = request.user.username
        rData["id"] = data["customerTypeId"]      
        rData["isConfigurable"] = data["isConfigurable"]
        rData["isVisible"] = data["isVisible"]                         
        rData["name"] = data["customerTypeName"]
        rData["typeDescription"] = data["customerTypeDesc"]
        rData["param"] = data["params"]
        rData["paramDescription"] = data["paramsDesc"]
        rData["projectName"] = data["projectName"]                  
        
    client = Client(url,retxml = True)

    #Call Fucntion
    UserIDPrefix = client.service.EnableDisableCustomerType(rData)

    #Convert xml to dict
    results =  xmltodict.parse(UserIDPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['EnableDisableCustomerTypeResponse']['EnableDisableCustomerTypeResult']             
         
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':   
                   
        values = {"status" : responseCode, "message": message, "result": result}  

    else:

        values = {"errorReason": errorReason}
            
    return HttpResponse(json.dumps(values), content_type='application/json')

def addQuery(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
        
        rData["dataBaseId"] = data["dataBaseId"]
        rData["sqlCommand"] = data["sqlCommand"]
        rData["customerType"] = data["customerTypeName"]
        rData["selectListItem"] = data["selectListItem"]
        rData["tableListItem"] = data["tableListItem"]                
        rData["alias"] = data["alias"]
        rData["joinCondition"] = data["joinCondition"]
        rData["filterCondition"] = data["filterCondition"]
        rData["filterParam"] = data["filterParam"]
        rData["selfDefinedSQLQuery"] = data["selfDefinedSQLQuery"]   
        rData["changeBy"] = request.user.username          
   
    client = Client(url,retxml = True)

    #Call Fucntion
    Query = client.service.AddQuery(rData)

    #Convert xml to dict
    results =  xmltodict.parse(Query)

    data = json.loads(json.dumps(results))
    
    result = data['s:Envelope']['s:Body']['AddQueryResponse']['AddQueryResult']['a:result']
    
    message = data['s:Envelope']['s:Body']['AddQueryResponse']['AddQueryResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['AddQueryResponse']['AddQueryResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['AddQueryResponse']['AddQueryResult']['a:responseCode']
    
    if responseCode == 'Success':
        
        values = {"result": result, "message" : message, "responseCode": responseCode}

    else:

        values = {"errorReason": errorReason}
        
    return HttpResponse(json.dumps(values), content_type='application/json')

def updateQuery(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                

        rData["sqlCommand"] = data["sqlCommand"]
        rData["customerType"] = data["customerTypeName"]
        rData["selectListItem"] = data["selectListItem"]
        rData["tableListItem"] = data["tableListItem"]                
        rData["alias"] = data["alias"]
        rData["joinCondition"] = data["joinCondition"]
        rData["filterCondition"] = data["filterCondition"]
        rData["filterParam"] = data["filterParam"]
        rData["id"] = data["subQueryId"]
        rData["selfDefinedSQLQuery"] = data["selfDefinedSQLQuery"]   
        rData["changeBy"] = request.user.username          
        print(str(rData))
    client = Client(url,retxml = True)    

    #Call Fucntion
    Query = client.service.UpdateQuery(rData)

    #Convert xml to dict
    results =  xmltodict.parse(Query)

    data = json.loads(json.dumps(results))
    
    result = data['s:Envelope']['s:Body']['UpdateQueryResponse']['UpdateQueryResult']['a:result']
    
    message = data['s:Envelope']['s:Body']['UpdateQueryResponse']['UpdateQueryResult']['a:message']

    errorReason = data['s:Envelope']['s:Body']['UpdateQueryResponse']['UpdateQueryResult']['a:errorReason']
    
    responseCode = data['s:Envelope']['s:Body']['UpdateQueryResponse']['UpdateQueryResult']['a:responseCode']
    
    if responseCode == 'Success':
        
        values = {"result": result, "message" : message, "responseCode": responseCode}

    else:

        values = {"errorReason": errorReason}
        
    return HttpResponse(json.dumps(values), content_type='application/json')

def enableDisableSubQuery(request):

    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["subQueryId"]
        rData["customerType"] = data["customerType"]
        rData["sqlCommand"] = data["sqlCommand"]
        rData["selectListItem"] = data["selectListItem"]
        rData["filterCondition"] = data["filterCondition"]
        rData["filterParam"] = data["filterParam"]
        rData["joinCondition"] = data["joinCondition"]
        rData["joinSequence"] = data["joinSequence"]
        rData["selfDefinedSQLQuery"] = data["selfDefinedSQLQuery"]
        rData["tableListItem"] = data["tableListItem"]
        rData["alias"] = data["alias"]
        rData["changeBy"] = request.user.username              
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EnableDisableQuery = client.service.EnableDisableQuery(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EnableDisableQuery)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['EnableDisableQueryResponse']['EnableDisableQueryResult']             
              
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
    
        values = {"status" : responseCode, "message": message, "result": result}

    else: 

        values = {"errorReason": errorReason}   
            
    return HttpResponse(json.dumps(values), content_type='application/json')

def addProductMapByProject(request):
   
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
                     
        rData["id"] = ''
        rData["dataBaseId"] = data["dataBaseId"]
        rData["name"] = data["productTypeName"]
        rData["productKey"] = data["productKey"]
        rData["ipsProductKey"] = data["ipsProductKey"]                        
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username          
   
    client = Client(url,retxml = True)

    #Call Fucntion
    ProductMap = client.service.AddProductMap(rData)

    #Convert xml to dict
    results =  xmltodict.parse(ProductMap)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['AddProductMapResponse']['AddProductMapResult']             
                    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result}  

    else:

        values = {"errorReason": errorReason}         
            
    return HttpResponse(json.dumps(values), content_type='application/json')


def updateProductMapByProject(request):
   
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
                     
        rData["id"] = data["productTypeId"]
        rData["name"] = data["productTypeName"]
        rData["productKey"] = data["productKey"]
        rData["ipsProductKey"] = data["ipsProductKey"]                        
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username          
   
    client = Client(url,retxml = True)

    #Call Fucntion
    ProductMap = client.service.UpdateProductMap(rData)

    #Convert xml to dict
    results =  xmltodict.parse(ProductMap)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['UpdateProductMapResponse']['UpdateProductMapResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result}              

    else:

        values = {"errorReason": errorReason}        
            
    return HttpResponse(json.dumps(values), content_type='application/json')


def enableDisableProductMap(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                          
         
        rData["id"] = data["productTypeId"]
        rData["name"] = data["productTypeName"]
        rData["productKey"] = data["productKey"]
        rData["ipsProductKey"] = data["ipsProductKey"]                               
        rData["projectName"] = str(data["projectName"])           
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EnableDisableProductMap = client.service.EnableDisableProductMap(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EnableDisableProductMap)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['EnableDisableProductMapResponse']['EnableDisableProductMapResult']             
         
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result}  
    
    else: 

        values = {"errorReason": errorReason}
            
    return HttpResponse(json.dumps(values), content_type='application/json')


def addUserIDPrefixByProject(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
                 
        rData["name"] = data["userIdPrefixName"] 
        rData["dataBaseId"] = data["dataBaseId"]                      
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    UserIDPrefix = client.service.AddUserIDPrefix(rData)

    #Convert xml to dict
    results =  xmltodict.parse(UserIDPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['AddUserIDPrefixResponse']['AddUserIDPrefixResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result}  

    else: 

        values = {"errorReason": errorReason}    
                        
    return HttpResponse(json.dumps(values), content_type='application/json')

def updateUserIDPrefixByProject(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["userIdPrefixId"]
        rData["name"] = data["userIdPrefixName"]                       
        rData["projectName"] = data["projectName"]   
        #rData["IsEnable"] = data["IsEnable"]
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    UserIDPrefix = client.service.UpdateUserIDPrefix(rData)

    #Convert xml to dict
    results =  xmltodict.parse(UserIDPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['UpdateUserIDPrefixResponse']['UpdateUserIDPrefixResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message,  "result": result}

    else: 

        values = {"errorReason": errorReason}        
            
    return HttpResponse(json.dumps(values), content_type='application/json')


def enableDisableUserIDPrefix(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["userIdPrefixId"]
        rData["name"] = data["userIdPrefixName"]                       
        rData["projectName"] = data["projectName"]           
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EnableDisableUserIDPrefix = client.service.EnableDisableUserIDPrefix(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EnableDisableUserIDPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['EnableDisableUserIDPrefixResponse']['EnableDisableUserIDPrefixResult']                                
             
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result}

    else: 

        values = {"errorReason": errorReason}     
            
    return HttpResponse(json.dumps(values), content_type='application/json')


def addEmailPrefixByProject(request):        
    
    if(request.method=='POST'):                
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = ''
        rData["dataBaseId"] = data["dataBaseId"]
        rData["name"] = data["emailPrefixName"]                       
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EmailPrefix = client.service.AddEmailPrefix(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EmailPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['AddEmailPrefixResponse']['AddEmailPrefixResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result} 

    else: 

        values = {"errorReason": errorReason}                          
            
    return HttpResponse(json.dumps(values), content_type='application/json')

def updateEmailPrefixByProject(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["emailPrefixId"]
        rData["name"] = data["emailPrefixName"]                       
        rData["projectName"] = data["projectName"]           
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EmailPrefix = client.service.UpdateEmailPrefix(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EmailPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['UpdateEmailPrefixResponse']['UpdateEmailPrefixResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result} 

    else: 

        values = {"errorReason": errorReason}             
            
    return HttpResponse(json.dumps(values), content_type='application/json')

def enableDisableEmailPrefix(request):
    
    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["emailPrefixId"]
        rData["name"] = data["emailPrefixName"]                       
        rData["projectName"] = data["projectName"]           
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EnableDisableEmailPrefix = client.service.EnableDisableEmailPrefix(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EnableDisableEmailPrefix)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['EnableDisableEmailPrefixResponse']['EnableDisableEmailPrefixResult']             
              
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
    
        values = {"status" : responseCode, "message": message, "result": result}

    else: 

        values = {"errorReason": errorReason}   
            
    return HttpResponse(json.dumps(values), content_type='application/json')

def addPasswordRule(request):
    
    if(request.method=='POST'):                
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["passwordRuleId"]
        rData["dataBaseId"] = data["dataBaseId"]
        rData["userIdRegex"] = data["userIdRegex"]
        rData["userPassword"] = data["userPassword"]
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username               
   
    client = Client(url,retxml = True)

    #Call Fucntion
    PasswordRule = client.service.AddPasswordRule(rData)

    #Convert xml to dict
    results =  xmltodict.parse(PasswordRule)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['AddPasswordRuleResponse']['AddPasswordRuleResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result} 

    else: 

        values = {"errorReason": errorReason}                          
            
    return HttpResponse(json.dumps(values), content_type='application/json')

def updatePasswordRule(request):

    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["passwordRuleId"]
        rData["userIdRegex"] = data["userIdRegex"]
        rData["userPassword"] = data["userPassword"]
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username                
   
    client = Client(url,retxml = True)

    #Call Fucntion
    PasswordRule = client.service.UpdatePasswordRule(rData)

    #Convert xml to dict
    results =  xmltodict.parse(PasswordRule)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['UpdatePasswordRuleResponse']['UpdatePasswordRuleResult']             
    
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
                   
        values = {"status" : responseCode, "message": message, "result": result} 

    else: 

        values = {"errorReason": errorReason}             
            
    return HttpResponse(json.dumps(values), content_type='application/json')    

def enableDisablePasswordRule(request):

    if(request.method=='POST'):
                     
        data = json.loads(request.POST.get('myjsondata'))
        
        rData = {}                
         
        rData["id"] = data["passwordRuleId"]
        rData["userIdRegex"] = data["userIdRegex"]
        rData["userPassword"] = data["userPassword"]
        rData["projectName"] = data["projectName"]   
        rData["changeBy"] = request.user.username              
   
    client = Client(url,retxml = True)

    #Call Fucntion
    EnableDisablePasswordRule = client.service.EnableDisablePasswordRule(rData)

    #Convert xml to dict
    results =  xmltodict.parse(EnableDisablePasswordRule)

    data = json.loads(json.dumps(results))

    response = data['s:Envelope']['s:Body']['EnableDisablePasswordRuleResponse']['EnableDisablePasswordRuleResult']             
              
    responseCode = response['a:responseCode']
    
    message = response['a:message']

    errorReason = response['a:errorReason']
    
    result = response['a:result']

    if responseCode == 'Success':
    
        values = {"status" : responseCode, "message": message, "result": result}

    else: 

        values = {"errorReason": errorReason}   
            
    return HttpResponse(json.dumps(values), content_type='application/json')
