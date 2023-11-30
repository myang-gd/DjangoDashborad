 # auth/views.py

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
import requests
from django.db.models import Q
from cProfile import label
from django import forms
from apps.card_finder.models import Product
from suds.client import Client
import xmltodict
import json,datetime

service_host = 'gdcqatools01:82'
isProductMap = False
product_tuple_list = ()

def getProductMap(request):     

    datalist = []
    productMap = []
    product_List = []    
    product_tuple_list = ()

    client = Client('http://'+ service_host + '/CustomerFinderService/CustomerFinderService.svc?wsdl',retxml = True)

    #Call Fucntion
    productMap = client.service.LoadProductMaps(projectName = "", dataBaseId = 1) 

    #Convert xml to dict
    results =  xmltodict.parse(productMap)

    data = json.loads(json.dumps(results))    

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
                                                                                       
                productkey = {"Id" : Id, "productType" : productType, "productKey" : productKey, "ipsProductKey": ipsProductKey, "isEnable" : isEnable, "projectName" : projectName }

                product_tuple_list += ((productType, productType + ' (' + productKey + ')'),) 

            product_List.append(productkey)  
    
    else: 

        errorReason = {"errorReason":errorReason}      

        product_List.append(errorReason)

    if request.method == 'GET':
    
        return HttpResponse(json.dumps(product_List), content_type='application/json')        
                
    return productMap 


def card_finder(request):

    value = None
    jsonArray = None
    error = None
    product_list = None
    type = None
    product = None

    if request.POST.get('load_productmap') == 'true':
        isProductMap = True
    else:
        isProductMap = False    

    if request.POST:

        form = EnvironmentProductForm(request.POST)

        if (request.POST.get('load_products') != 'true' and request.POST.get('load_productmap') == 'true') or (request.POST.get('load_products') == 'true' and request.POST.get('load_productmap') != 'true'):            

            if 'get_sub' in request.POST:  # Got 'get' request

                type = 'get'
                environment = request.POST.get('environment')                
                if isProductMap == True:                    
                    product = request.POST.get('productmap')
                else:    
                    product = request.POST.get('product')
                value = request.POST.get('value')
                
                params = {'product': product, 'environment': environment, 'value': value}
                response = requests.get('http://' + service_host + '/cardfinderservice/CardFinderService.svc/get', params=params)                

                if response.status_code != 200:
                    if response.json() != None:
                        error = response.json()
                    else:
                        response.raise_for_status()
                else:
#                 if 'count_sub' in request.POST and product.upper() != 'Product (All)'.upper():
#                     jsonArray = [{'product': product, 'count': response.text}]
#                 else:
                    jsonArray = response.json()
                
                            
            if 'count_sub' in request.POST:  # Got 'count' request

                type = 'count'
                environment = request.POST.get('environment')                
                if isProductMap == True:                    
                    product = request.POST.get('productmap')                
                else:    
                    product = request.POST.get('product')
                #product_list = request.POST.get('product_list').strip()
                value = request.POST.get('value')

                if product_list is not None and product_list != "":
                    params = {'environment': environment, 'product': product_list}
                    response = requests.get('http://'  + service_host + '/cardfinderservice/CardFinderService.svc/count', params=params)
                else:
                    params = {'environment': environment, 'product': product}
                    response = requests.get('http://'  + service_host + '/cardfinderservice/CardFinderService.svc/count', params=params)
                    
                if response.status_code != 200:
                    if response.json() != None:
                        error = response.json()
                    else:
                        response.raise_for_status()
                else:
#                 if 'count_sub' in request.POST and product.upper() != 'Product (All)'.upper():
#                     jsonArray = [{'product': product, 'count': response.text}]
#                 else:
                    jsonArray = response.json()
       
    else:
                    
        form = EnvironmentProductForm()

    render_dict = {
        'form': form,
        'output': jsonArray,
        'value': value,
        'error': error,
        'product_list': product_list,
        'type': type,
        'isProductMap': isProductMap,
    }

    return render(request, 'card_finder.html', render_dict)

def populate_product_choices(env):
    
    if env == 'QA3':
        products = Product.objects.using('QA3').filter(Q(programkey=4) | Q(programkey=10) | Q(programkey=8))
    elif env == 'QA4':
        products = Product.objects.using('QA4').filter(Q(programkey=4) | Q(programkey=10) | Q(programkey=8))
    elif env == 'QA5':
        products = Product.objects.using('QA5').filter(Q(programkey=4) | Q(programkey=10) | Q(programkey=8))
    elif env == 'PIE':
        products = Product.objects.using('PIE').filter(Q(programkey=4) | Q(programkey=10) | Q(programkey=8))
    else:
        return ()
        
    product_tuple = ()
    
    for product in products:
        product_tuple += ((product.productcode, product.productcode + ' (' + product.productdescription + ')'),)
        
    return product_tuple

class EnvironmentProductForm(forms.Form):

    environments = (
#         ('', ''),
        ('QA3', 'QA3'),
        ('QA4', 'QA4'),
        ('QA5', 'QA5'),
        ('PIE', 'PIE'),
    )
        
    def __init__(self, *args, **kwargs):        
        super(EnvironmentProductForm, self).__init__(*args, **kwargs)
        if len(args) > 0:          

            if isProductMap:                           
                 self.fields['productmap'] = forms.ChoiceField(choices=product_tuple_list)
            else:    
                 self.fields['product'] = forms.ChoiceField(choices=populate_product_choices(args[0]['environment']))                                
                        
    environment = forms.ChoiceField(label='Environment', choices=environments)
#     environment.widget.attrs['style'] = 'width:350'
    product = forms.ChoiceField(label='Product')

