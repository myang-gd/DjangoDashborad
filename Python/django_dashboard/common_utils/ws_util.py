import logging
import requests
from requests.auth import HTTPBasicAuth
import urllib
from common_utils.constant import Constant, SOAP_VERSION
from xml.dom.minidom import parseString
from suds.client import Client
from suds import transport
from suds.transport.https import HttpAuthenticated
import ssl
from urllib.request import HTTPSHandler
import suds
from requests_ntlm import HttpNtlmAuth
import httplib2
import random
import string
import uuid
import json
from urllib.parse import urlparse


class CustomTransport(HttpAuthenticated):

    def u2handlers(self):
        # use handlers from superclass
        handlers = HttpAuthenticated.u2handlers(self)

        ctx = ssl._create_unverified_context()
        # configure context as needed...
        ctx.check_hostname = False
       
        # add a https handler using the custom context
        handlers.append(HTTPSHandler(context=ctx))
        return handlers 

class WSUtil:
    POST,GET = ('post','get')
    XML,JSON, URLENCODED = ('xml', 'json', 'urlencoded')
    REGEX,PLAIN = ('regex','plain')
    @classmethod
    def processRestRequest(cls, url, message, validations=None, headers=None, method=GET, verify=False, message_type=JSON, surpass_headers=None, timeout=None, **kwargs):
        user = kwargs.get('user')
        password = kwargs.get('password')
        if user and password:
            auth = HTTPBasicAuth(user, password)
        else:
            auth = None
        if message and message.strip().lower() == "null":
            message = '';
        validationResult = {}
        result = {}
        response = "";
        if not method:
            raise Exception("Argument method can't be none") 
        header_map = {} 
        header_str = ''
        try:
            input_headers = cls.get_header_dic(headers)
            for key in input_headers:
                header_map[key] = input_headers[key]
            if surpass_headers:
                for key in surpass_headers:
                    header_map[key] = surpass_headers[key]
            header_str = json.dumps(header_map, sort_keys=True, indent=4) 
            if method.strip().lower() == cls.GET.lower():
                url = url + message
                if headers:
                    response = requests.get(url, headers = header_map, verify=verify, timeout=timeout, auth = auth)
                else:
                    response = requests.get(url, verify=verify, auth = auth) 
            elif method.strip().lower() == cls.POST.lower():
                if message_type.lower() == cls.XML.lower():
                    header_map['Content-type'] = 'application/xml'
                    response = requests.post(url, data=message,headers=header_map,verify=verify,timeout=timeout)  
                elif message_type.lower() == cls.URLENCODED.lower():
                    header_map['Content-type'] = 'application/x-www-form-urlencoded'
                    response = requests.post(url, data=message,headers=header_map,verify=verify,timeout=timeout)
                else:
                    header_map['Content-type'] = 'application/json'
                    response = requests.post(url, json=json.loads(message),headers=header_map,verify=verify,timeout=timeout)
                
            result[Constant.REQUEST] = message
            result[Constant.ERROR] = ''
            response.raise_for_status()
           
            jsonArray = None

            if message_type.lower() == cls.XML.lower() or message_type.lower() == cls.URLENCODED.lower():
                result[Constant.RESPONSE] = response.text
                result[Constant.VALIDATION_RESULT] = ''
            else:
                jsonArray = response.json()
            result[Constant.TEXT] = response.text
            
            success = Constant.Y             
            if validations==None:
                success = Constant.Y                
            elif jsonArray :   
                for validation in validations.split(','):
                    if "=" not in validation:
                        continue
                    key, value = validation.split("=")
                    if key.strip() in jsonArray:
                        if (jsonArray[key.strip()].strip() != value.strip()):
                            validationResult[str(validation)] = Constant.FAILED
                        else:
                            validationResult[str(validation)] = Constant.PASSED
                    else:
                        validationResult[str(validation)] = Constant.FAILED
                result[Constant.RESPONSE] = json.dumps(jsonArray, sort_keys=True, indent=4)
                result[Constant.VALIDATION_RESULT] = str(validationResult)  
            result[Constant.HEADERS] = header_str                      
            result[Constant.SUCCESS] = success
            return result
        except requests.exceptions.HTTPError as e:
            validationResult[Constant.ERROR] = "True"         
            return {Constant.SUCCESS: Constant.N, Constant.ERROR: str(response), Constant.RESPONSE: str(e), Constant.VALIDATION_RESULT:str(validationResult),
                    Constant.REQUEST: message, Constant.HEADERS: header_str }
    @classmethod        
    def processSoapRequest(cls, url, method, port, message, user=None, password=None, validations=None, vip_name=None, timeout=None):     
        logger = logging.getLogger("healthcheck")
        soap_version = SOAP_VERSION.SOAP_1_1 
        if "http://www.w3.org/2003/05/soap-envelope" in message:
            soap_version = SOAP_VERSION.SOAP_1_2
        
        # Check if given URL is valid and exists
        
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            urllib.request.urlopen(url,context=ctx,timeout=timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            if 'HTTP Error 401: Unauthorized' not in str(e):
                validationResult = {}
                validationResult[Constant.INVALID_WSDL_URL] = Constant.FAILED
                logger.error("Exception happened when calling SOAP Request: " + url + ", method: " + str(method) + ", message: " + str(message))
                return {Constant.SUCCESS: Constant.N, Constant.ERROR: '', Constant.RESPONSE: str(e) + " - " + url, Constant.VALIDATION_RESULT:str(validationResult),
                        Constant.REQUEST: message}
        if soap_version == SOAP_VERSION.SOAP_1_1:
            responseMessageOriginal = cls.processSoapRequest1_1(url, method, port, message, user=user, password=password, vip_name=vip_name)
        elif soap_version == SOAP_VERSION.SOAP_1_2:
            responseMessageOriginal = cls.processSoapRequest1_2(url, message, user=user, password=password, vip_name=vip_name)
                
        responseMessage = ''        
        try:
            responseMessage = parseString(responseMessageOriginal).toprettyxml()
        except:
            responseMessage = responseMessageOriginal
        print(responseMessage)
        success = Constant.Y
        if validations==None:
            success = Constant.Y
        else:
            validationResult = {}
            for validation in validations.split(','):
                if validation and validation.strip() not in str(responseMessage):
                    success = Constant.N
                    validationResult[str(validation)] = Constant.FAILED
                else:
                    validationResult[str(validation)] = Constant.PASSED
        error = ''
        logger.info("Returning soap response message: " + str(responseMessage))
        return {Constant.SUCCESS: success, Constant.ERROR: str(error), Constant.RESPONSE: str(responseMessage), Constant.VALIDATION_RESULT:str(validationResult),
                Constant.REQUEST: message}
    
    @classmethod 
    def processSoapRequest1_2(cls, url, message, user=None, password=None, vip_name=None):
        """Process soap 1.2 request. """ 
        if vip_name:
            headers={'content-type': 'application/soap+xml;charset=UTF-8;', 'Host':vip_name}
        else:
            headers={'content-type': 'application/soap+xml;charset=UTF-8;'}
    
        message = message.encode(encoding='utf_8', errors='strict')
    
        try:
            if user and user.strip() and password and password.strip():
                session = requests.Session()
                session.auth =HttpNtlmAuth(user,password, session)
                response = session.post(url,data=message,headers=headers)
            else: 
                response = requests.post(url,data=message,headers=headers)
        except requests.exceptions.RequestException as e:
            responseMessage = str(e)
        else:
            if response is not None:
                if response.status_code != 200:
                    responseMessage = ('%s Reason: %s' %(str(response),response.reason))
                else:                
                    responseMessage = response.content.decode(Constant.UTF8)
            else:
                responseMessage = ''  
        return responseMessage   
    @classmethod 
    def sendPTSRequest(cls, url, body, cert, key, headers:dict=None):
        if not headers:
            headers = {'content-type': 'text/xml;charset=UTF-8', 'SOAPAction':''}
        body_str = cls.bodyReset(body)
        body = body_str.encode(encoding='utf_8', errors='strict')
        http = httplib2.Http(timeout=60)
        hostname = urlparse(url).hostname
        port = urlparse(url).port
        
        http.add_certificate(key, cert, domain=('%s:%s' % (hostname,port)))
        try:
            (response, content) = http.request(url, 'POST', body=body, headers=headers) 
            if type(content) is bytes:
                responseMessage = content.decode(Constant.UTF8)
                success = Constant.Y
            else:
                responseMessage =  'PTS response is not bytes'
                success = Constant.N
        except Exception as e: 
                responseMessage = 'Exception was catched for PTS request ' + str(e)
                success = Constant.N
            
        return {Constant.SUCCESS: success, Constant.ERROR: '', Constant.RESPONSE: str(responseMessage), Constant.VALIDATION_RESULT:'',
                Constant.REQUEST: body_str}
    @classmethod
    def id_generator(cls, size=30, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @classmethod 
    def bodyReset(cls, requestBody):
        prefix_str = cls.id_generator(25)
        postfix_num = int(str(uuid.uuid4().int)[-7:])
    
        requestBody = requestBody.replace('[URI]', prefix_str + str(postfix_num))
        requestBody = requestBody.replace('[X509ID]', prefix_str + str(postfix_num))
        requestBody = requestBody.replace('[KI]', prefix_str + str(postfix_num+1))
        requestBody = requestBody.replace('[STR]', prefix_str + str(postfix_num+2))
        return requestBody

    @classmethod 
    def processSoapRequest1_1(cls, url, method, port, message, user=None, password=None, vip_name=None):
        """Process soap 1.1 request. """ 
        if user and user.strip() and password and password.strip():
            client = Client(url, transport=transport.https.WindowsHttpAuthenticated(username=user, password = password), faults=False, retxml = True)
        else:
            client = Client(url, faults=False, retxml = True, transport=CustomTransport())
        if vip_name:
            client.set_options(headers={'Host':vip_name})
        if port:
            client.set_options(port=port)  
        _message = message.encode(encoding=Constant.UTF8, errors='strict')
        try:
            function=getattr(client.service,method) 
        except Exception as e:
            return ('Method %s not found in this service, exception: %s' % (method,str(e)))
        if type(function) is suds.client.Method:
            responseMessage = function(__inject={'msg':_message})
            if type(responseMessage) == type(()):
                # response code is not 200
                responseMessage =  str(responseMessage) 
            else:
                responseMessage = responseMessage.decode(Constant.UTF8)
        else:
            responseMessage = 'Wrong action type'
            
        return responseMessage
    @classmethod
    def get_header_dic(cls,headers)-> dict:
        if headers and headers.strip():
            headers = dict(item.split("=", 1) for item in headers.split(",")) # Convert comma seperated header to python dictionary
            headers = {key.strip(): item.strip() for key, item in headers.items()} # Clean up headers from \n \r (special characters)    
            return  headers
        else: 
            return {}