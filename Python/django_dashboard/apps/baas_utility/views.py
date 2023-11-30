from django.http import HttpResponse
from django.shortcuts import render
import xmltodict
import json
from suds.client import Client
from datetime import datetime

url = "http://gdcqatools01:82/CustomerFinderService/CustomerFinderService.svc?wsdl"

def baas_utility(request):
                           
    return render(request, 'baas_utility.html')


def get_card_info(request):
    if request.is_ajax():
        pan = ""
        exp_date = ""
        cvv = ""
        ssn = ""
        dob = ""
        error = ""
        response_code = ""
         
        env = request.POST.get('env')
        tokenized_pan = request.POST.get('tokenized_pan')
        payment_instrument_type = request.POST.get('payment_instrument_type')
        
        if env != "Environment":
            if payment_instrument_type != "Payment Instrument Type":
                if tokenized_pan != "":
                    client = Client(url, retxml = True)
                    
                    get_card_info = client.service.GetCardInfo(env = str(env), tokenizedPAN = str(tokenized_pan), paymentInstrumentType = str(payment_instrument_type))
            
                    result =  xmltodict.parse(get_card_info)
            
                    data = json.loads(json.dumps(result))
        
                    response_code = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:responseCode']
        
                    if str(response_code) == "Success":
                        pan = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:result']['b:pan']
                        exp_date = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:result']['b:expDate']
                        cvv = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:result']['b:cvv']
                        ssn = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:result']['b:ssn']
                        dob = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:result']['b:dob']
                    else:
                        error = data['s:Envelope']['s:Body']['GetCardInfoResponse']['GetCardInfoResult']['a:errorReason']
                else:
                    response_code = "Failed"
                    error = "Please input Tokenized PAN!"
            else:
                response_code = "Failed"
                error = "Please select Payment Instrument Type!"
        else:
            response_code = "Failed"
            error = "Please select Environment!"
        
        if response_code == "Success":
            output = {'PAN': str(pan), 'ExpDate': str(exp_date)[0:2] + "/" + str(exp_date)[2:6], 'CVV': str(cvv), 'SSN': str(ssn), 'DOB': datetime.strptime(dob, '%Y-%m-%d').strftime("%m-%d-%Y"), 'Error': str(error), 'ResponseCode': str(response_code)}
        else:
            output = {'PAN': "", 'ExpDate': "", 'CVV': "", 'SSN': "", 'DOB': "", 'Error': str(error), 'ResponseCode': str(response_code)}
        return HttpResponse(json.dumps({'Output': output}), content_type='application/json')
    else:
        pass
        
        
        
        
        
        
        