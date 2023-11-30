from django.http import HttpResponse
from django.shortcuts import render
import xmltodict
import json
from suds.client import Client
from datetime import datetime
from pyasn1.compat.octets import null

url = "http://gdcqatools01:82/CustomerFinderService/CustomerFinderService.svc?wsdl"

def dmwn_card_finder(request):
    
    return render(request, 'dmwn_card_finder.html')

def get_card_details(request):
    if request.is_ajax():
        pan = ""
        exp_date = ""
        cvv = ""
        ssn = ""
        dob = ""
        card_proxy = ""
        error = ""
        response_code = ""
         
        env = request.POST.get('env')
        product_code = request.POST.get('product_code')
        customer_acquisition_type = request.POST.get('customer_acquisition_type')
        is_emv = request.POST.get('is_emv')
        
        if env != "Environment":
            if customer_acquisition_type != "Customer Acquisition Type":
                if product_code != "":
                    client = Client(url, retxml = True)
                    
                    get_card_details = client.service.GetCardDetails(env = str(env), productCode = str(product_code), customerAcquisitionType = str(customer_acquisition_type), isEMV = is_emv)
            
                    result =  xmltodict.parse(get_card_details)
            
                    data = json.loads(json.dumps(result))
        
                    response_code = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:responseCode']
#                     print(data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result'])
                    if str(response_code) == "Success":
                        pan = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:pan']
                        exp_date = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:expDate']
                        cvv = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:cvv']
                        ssn = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:ssn']
                        last4ssn = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:last4ssn']
                        dob = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:dob']
                        card_proxy = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:result']['b:cardProxy']
                    else:
                        error = data['s:Envelope']['s:Body']['GetCardDetailsResponse']['GetCardDetailsResult']['a:errorReason']
                else:
                    response_code = "Failed"
                    error = "Please input Product Code!"
            else:
                response_code = "Failed"
                error = "Please select Customer Acquisition Type!"
        else:
            response_code = "Failed"
            error = "Please select Environment!"
        
        if ssn == None:
            ssn = ""
        
        if dob != None and dob != "":
            dob = datetime.strptime(dob, '%Y-%m-%d').strftime("%m-%d-%Y")
        else:
            dob = ""
            
        output = {'PAN': str(pan), 'ExpDate': datetime.strptime(exp_date, '%Y%m%d').strftime("%m-%d-%Y"), 'CVV': str(cvv), 'SSN': str(ssn), 'Last4SSN': str(last4ssn), 'DOB': str(dob), 'CardProxy': str(card_proxy), 'Error': str(error), 'ResponseCode': str(response_code)}
#         print(output)
        return HttpResponse(json.dumps({'Output': output}), content_type='application/json')
    else:
        pass