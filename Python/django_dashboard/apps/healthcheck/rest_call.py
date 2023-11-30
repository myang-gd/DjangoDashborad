'''
Created on Feb 25, 2016

@author: zbasmajian
'''
import requests

'''
url = 'http://partners.greendotonline.com/gateway/V2/clientaccountoperations/registrations/1390645'
headers = {'RequestID': '654894', 'Authorization': 'Basic TkVYVEVTVEFURVxJbnR1aXQ6SW50dWl0U2lnbnVw'}

response = requests.get(url, headers = headers)

if response.status_code != 200:
    if response.json() != None:
        error = response.json()
        print(error)
    else:
        response.raise_for_status()
else:
    jsonArray = response.json()
    print(jsonArray)
   
''' 




headers = "Authorization = Basic Z2RjcGZuZHVzZXI6SC9sVFBpa0ZNSGtHekdNQW9uOHQ2Y1JxZEdNPQ==,  endusersecurityid = 1234_Test,requestid = 20194767388632,partneridentifier = GDCPreFund, enduserip = 10.23.21.21"
headers = dict(item.split("=", 1) for item in headers.split(","))
print(headers)









'''
url2 = 'https://qa4-partners.greendotcorp.com/Disbursements/api/v1/customers/vv1234'
headers2 = {'Authorization' : 'Basic Z2RjcGZuZHVzZXI6SC9sVFBpa0ZNSGtHekdNQW9uOHQ2Y1JxZEdNPQ==', 
            'endusersecurityid':'1234_Test', 
            'requestid':'20194767388632', 
            'partneridentifier':'GDCPreFund', 
            'enduserip':'10.23.21.21'}

response2 = requests.get(url2, headers = headers2)

            
try:
    if response2.status_code != 200:
        response2.raise_for_status()
    else:
        responseJson = response2.json()
        validations = "responsemessage = Success"
        validationResult = {}
        for validation in validations.split(','):
            validationKeyValuePair = validation.split("=")
            if (responseJson[validationKeyValuePair[0].strip()].strip() != validationKeyValuePair[1].strip()):
                success='N'
                validationResult[str(validation)] = 'Failed'
            else:
                validationResult[str(validation)] = 'Passed'
            
            if response2.status_code != 200:
                error = responseJson
            else:
                error = ''
        
        
except requests.exceptions.HTTPError as e:
        print(str(e))
'''
