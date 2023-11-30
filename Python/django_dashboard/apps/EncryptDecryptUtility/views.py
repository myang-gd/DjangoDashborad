from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.shortcuts import render
import xmltodict
import json
from suds.client import Client
from time import sleep
import traceback
import requests
from requests_ntlm import HttpNtlmAuth
import ssl

url = "http://gdcqatools01:82/CustomerFinderService/CustomerFinderService.svc?wsdl"
PersonalIDTokenizeUrl = "https://tknsvc/PersonalIdTokenizer/v1/Tokenize"
PersonalIDDeTokenizeUrl = "https://tknsvc/PersonalIdTokenizer/v1/Detokenize"

def EncryptDecryptUtility(request):
                           
    return render(request, 'EncryptDecryptUtility.html')   

def TokenizationUtility(request):
                           
    return render(request, 'TokenizationUtility.html')    

def encryptDecrypt(request):
    if request.is_ajax():
        cipher_text = ""
        error = ""
        response_code = ""
        errorReason = ""
         
        project_name = request.POST.get('project_name')
        encode_decode_type = request.POST.get('encode_decode_type')
        encode_decode_string = request.POST.get('encode_decode_string')
        
        if project_name != "" and project_name != None:
            if encode_decode_string != "":
                client = Client(url, retxml = True)
        
                get_cipher_text = client.service.GetEncryptDecryptResult(passPhrase = str(project_name), encodeDecodeString = str(encode_decode_string), encodeDecodeType = int(encode_decode_type))
            
                result =  xmltodict.parse(get_cipher_text)
            
                data = json.loads(json.dumps(result))
        
                response_code = data['s:Envelope']['s:Body']['GetEncryptDecryptResultResponse']['GetEncryptDecryptResultResult']['a:responseCode']
        
                if str(response_code) == "Success":
                    cipher_text = data['s:Envelope']['s:Body']['GetEncryptDecryptResultResponse']['GetEncryptDecryptResultResult']['a:result']
                else:
                    errorReason = data['s:Envelope']['s:Body']['GetEncryptDecryptResultResponse']['GetEncryptDecryptResultResult']['a:errorReason']
                    
            else:
                response_code = "Failed"
                error = "Please input text you want encrypt or decrypt!"
        else:
            response_code = "Failed"
            error = "Please select Project!"
        
        output = {'CipherText': str(cipher_text), 'errorReason': str(errorReason), 'ResponseCode': str(response_code)}

        return HttpResponse(json.dumps({'Output': output}), content_type='application/json')
    else:
        pass 
        
 
def Tokenize(request):
    print("I'm here")
    PersonalId = request.POST.get("PersonalId")                
    CallChainID = request.POST.get('CallChainID') 
     
    headers = {} 
    headers['Content-type'] = 'application/json'

    data = {};
    data["PersonalId"] = PersonalId
    data["CallChainID"] = CallChainID

    session = requests.Session()
    session.auth = HttpNtlmAuth("nextestate\\svcpvqa","Greendot1")
    response = session.post(PersonalIDTokenizeUrl,json=data,headers=headers,verify=False)
    response_str = str(response.content)[2:-1]
    response_json = json.loads(response_str)
   
    #print(str(response_json))

    return HttpResponse(json.dumps({'Output': response_json}), content_type='application/json')
    
    
        
def DeTokenize(request):
    PersonalIdToken = request.POST.get('PersonalIdToken')                

    headers = {} 
    headers['Content-type'] = 'application/json'

    data = {};
    data["PersonalIdToken"] = PersonalIdToken

    session = requests.Session()
    session.auth = HttpNtlmAuth("nextestate\\svcpvqa","Greendot1")
    response = session.post(PersonalIDDeTokenizeUrl,json=data,headers=headers,verify=False)
    response_str = str(response.content)[2:-1]
    response_json = json.loads(response_str)
    
    #print(str(response_json))

    return HttpResponse(json.dumps({'Output': response_json}), content_type='application/json')
    
        
def getProjects(request):
     
    print("start")


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


    for list in datalist:

        projects = list['b:KeyValueOfstringstring']

        for key,value in projects:

            projectId = int(projects[0]['b:Value'])

            projectName = projects[1]['b:Value']

            proj = {"Id":projectId,"projectName":projectName}

        project_list.append(proj)            

        print(str(project_list))
    
    if request.method == 'GET':
             
        return HttpResponse(json.dumps(project_list), content_type='application/json')                        
        
        
                