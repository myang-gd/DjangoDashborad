# from django.test import TestCase
# import requests
# # Create your tests here.
# from xmljson import BadgerFish
# from xmljson import GData as gd
# from xmljson import Yahoo as yh
# from xmljson import Parker as pk
# import xmltodict
# from collections import OrderedDict
# import http.client as hc
# import urllib
# from suds.client import Client
# from _overlapped import NULL
# import json,datetime
# from json import *
# from ldap3.operation.search import ROOT
# from xml.etree.ElementTree import fromstring
# #from .views import *

# def test():
    
#     #Service Url
#     url = 'http://pas-vxi-112.nextestate.com/test/CustomerFinderService.svc?wsdl'

#     #Initialize Parameters
#     #--------------------------------------------------------------- env = 'QA4'
#     #-------------------------------------------------------- products = 'GDC30'
#     #-------------------------------------------------------- custtypes = 'Temp'
#     #---------------------------------------------------------------- email = ''
#     #---------------------------------------------------- appendExtendQuery = ''
#     #--------------------------------------------------------------- project = 9
#     #------------------------------------------------------------- isips = False

    
                     
      
#     rData = {}  
#     rData["changeBy"] = "ddd"   
#     rData["isConfigurable"] = True
#     rData["isVisiable"] = True              
#     rData["id"] = '0'
#     rData["name"] = 'Dave'
#     rData["param"] = 'sdsds'
#     rData["projectId"] = '9'   

#     client = Client(url,retxml = True)

#     #Call Fucntion
# #     addCustType = client.service.AddCustomerType(changeBy = 'wchen', id = '0', isConfigurable = True, isVisiable = True, name = 'dava', param = 'sdsds',  projectId = '9')
#     addCustType = client.service.AddCustomerType(rData)

#     #Convert xml to dict
#     results =  xmltodict.parse(addCustType)

#     data = json.loads(json.dumps(results))

#     customer = data['s:Envelope']['s:Body']['AddCustomerTypeResponse']['AddCustomerTypeResult']
             
    
#     #output = customer['a:output']
                
#     customerinfo = {"customerkey" : customer}      
        
#     return customerinfo
    
#    # print(project_list)
    
# def getCusttypeMapList():
    
#     datalist = []
#     custTypes = []
#     custtype_List = []
#     customerType = {}

#     url = 'http://pas-vxi-112.nextestate.com/test/CustomerFinderService.svc?wsdl'

#     client = Client(url,retxml = True)
    
#     project = 9

#     #Call Fucntion
#     custTypes = client.service.LoadCustomerTypes(projectId=str(project))

#     #Convert xml to dict
#     results =  xmltodict.parse(custTypes)

#     data = json.loads(json.dumps(results))

#     datalist = data['s:Envelope']['s:Body']['LoadCustomerTypesResponse']['LoadCustomerTypesResult']['a:ArrayOfKeyValueOfstringstring']

#     for list in datalist:

#         custTypes = list['a:KeyValueOfstringstring']

#         for key,value in custTypes:

#             custType = custTypes[1]['a:Value']

#             customerType = {"custType":custType}

#         custtype_List.append(customerType)
        
#     return custtype_List            
#     #----------------------------------------------- if request.method == 'GET':
# #------------------------------------------------------------------------------ 
#         # return HttpResponse(json.dumps(custtype_List), content_type='application/json')
    
    

# def getCustomerTypeList():
    
#     customer = test()
    
#     print(customer)    
   
    
# getCustomerTypeList()