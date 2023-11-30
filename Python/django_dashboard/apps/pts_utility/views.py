from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.shortcuts import render
import xmltodict
import json
from suds.client import Client
from time import sleep
import traceback

url = "http://gdcqatools01:82/CustomerFinderService/CustomerFinderService.svc?wsdl"
# url = "http://localhost:60860/CustomerFinderService.svc?wsdl"
def pts_utility(request):
                           
    return render(request, 'pts_utility.html')


def get_cvv(request):
    if request.is_ajax():
        cvv = ""
        error = ""
        response_code = ""
         
        env = request.POST.get('env')
        serial_nbr = request.POST.get('serial_nbr')
        
        if env != "Environment":
            if serial_nbr != "":
                client = Client(url, retxml = True)
        
                get_cvv = client.service.GetCVV(env = str(env), serialNbr = str(serial_nbr))
            
                result =  xmltodict.parse(get_cvv)
            
                data = json.loads(json.dumps(result))
        
                response_code = data['s:Envelope']['s:Body']['GetCVVResponse']['GetCVVResult']['a:responseCode']
        
                if str(response_code) == "Success":
                    cvv = data['s:Envelope']['s:Body']['GetCVVResponse']['GetCVVResult']['a:result']['b:cvv']
                else:
                    error = data['s:Envelope']['s:Body']['GetCVVResponse']['GetCVVResult']['a:errorReason']
                    
            else:
                response_code = "Failed"
                error = "Please input SerialNbr!"
        else:
            response_code = "Failed"
            error = "Please select Environment!"
        
        output = {'CVV': str(cvv), 'Error': str(error), 'ResponseCode': str(response_code)}
#         print(output)
        return HttpResponse(json.dumps({'Output': output}), content_type='application/json')
    else:
        pass
    
def get_pts_card_info(request):
    if request.is_ajax():
        pts_card_info = []
        error = ""
        response_code = ""
         
        env = request.POST.get('env')
        serial_nbr = request.POST.get('serial_nbr')
        
        if env != "Environment":
            if serial_nbr != "":
                client = Client(url, retxml = True)
        
                pts_card_info = client.service.GetPTSCardInfo(env = str(env), serialNbr = str(serial_nbr))
            
                result =  xmltodict.parse(pts_card_info)
            
                data = json.loads(json.dumps(result))
#                 print("CardInfo=" + str(json.dumps(data)))
                response_code = data['s:Envelope']['s:Body']['GetPTSCardInfoResponse']['GetPTSCardInfoResult']['a:responseCode']
        
                if str(response_code) == "Success":
                    pts_card_info = data['s:Envelope']['s:Body']['GetPTSCardInfoResponse']['GetPTSCardInfoResult']['a:result']['b:PTSCardInfo']
                else:
                    error = data['s:Envelope']['s:Body']['GetPTSCardInfoResponse']['GetPTSCardInfoResult']['a:errorReason']
                    
            else:
                response_code = "Failed"
                error = "Please input SerialNbr!"
        else:
            response_code = "Failed"
            error = "Please select Environment!"
        
        output = {'PTSCardInfo': pts_card_info, 'Error': str(error), 'ResponseCode': str(response_code)}
#         print(output)
        return HttpResponse(json.dumps({'Output': output}), content_type='application/json')
    else:
        pass
        
        
        
        
        
        
        