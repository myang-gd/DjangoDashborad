import logging
import suds
from suds.client import Client
from suds.sax.text import Raw
from suds.sax.element import Element 
from suds.sax.parser import Parser
from suds.sax.document import Document
from suds import transport
from suds import null
import uuid
import datetime
import time
from suds.sax.text import Raw
import sys

# Logging to capture what it is being sent in request message
handler = logging.StreamHandler(sys.stderr)
logger = logging.getLogger('suds.transport.http')
logger.setLevel(logging.DEBUG), handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class OutgoingFilter(logging.Filter):
    def filter(self, record):
        return record.msg.startswith('sending')
 
handler.addFilter(OutgoingFilter())

## Non-V3 Service Call
'''
url = 'http://gdcsvc/Entity/Bank/BankService?WSDL'
client = Client(url)
gdcApplicationIdNS = ('ns0', 'http://greendotcorp.com/services/entity/Bank/v1') 
gdcApplicationId = Element('X-GDC-ApplicationID', ns=gdcApplicationIdNS).setText('8017')

client.set_options(port='BasicHttpBinding_IBank', soapheaders=(gdcApplicationId))
GetAddressRequest = client.factory.create('ns2:GetAddressRequest')
applicationType = client.factory.create('ns1:ApplicationType')
GetAddressRequest.BankToken = 5
GetAddressRequest.ApplicationType = applicationType.Web
result = client.service.GetAddress(GetAddressRequest)
'''

'''
## V3 Service Call
user = 'nextestate\svc_QA_V3Test'
password = "Greendot1"

v3client = Client(url='http://gdcsvcv3/Product/Product.svc?wsdl', transport=transport.https.WindowsHttpAuthenticated(username=user, password = password))
v3client.set_options(port='ProductService.Product.Endpoint')
GetProductRequest = v3client.factory.create('ns3:GetProductRequest')
GetProductRequest.ProductCode = '1424'
GetProductRequest.ProductKey = null()
GetProductRequest.ProductName = null()
v3Result = v3client.service.GetProduct(GetProductRequest)
'''

user = 'nextestate\svc_QA_V3Test'
password = "Greendot1"

v3client = Client(url='http://gdcsvcv3/Product/Product.svc?wsdl', transport=transport.https.WindowsHttpAuthenticated(username=user, password = password), retxml=True)
v3client.set_options(port='ProductService.Product.Endpoint')


message = \
"""<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:ns1="http://Product.GreendotCorp.com/Product" 
xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">
<SOAP-ENV:Header/><ns0:Body><ns1:GetProduct><ns1:request><ns2:ProductCode>1424</ns2:ProductCode><ns2:ProductKey xsi:nil="true"/>
<ns2:ProductName xsi:nil="true"/></ns1:request></ns1:GetProduct></ns0:Body></SOAP-ENV:Envelope>""".encode(encoding='utf_8', errors='strict')
responseMessage = v3client.service.GetProduct(__inject={'msg':message})
print(responseMessage)
#print(responseMessage.Products.Product[0].Bank.Name)
print('Name = "Green Dot Bank"' in str(responseMessage))
print('PostalCode = "84604"' in str(responseMessage))

message2 = \
"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prod="http://Product.GreendotCorp.com/Product">
   <soapenv:Header/>
   <soapenv:Body>
      <prod:GetFees>
         <prod:request>
            <gdot:ProductKey xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">2181</gdot:ProductKey>
         </prod:request>
      </prod:GetFees>
   </soapenv:Body>
</soapenv:Envelope>""".encode(encoding='utf_8', errors='strict')
responseMessage2 = v3client.service.GetFees(__inject={'msg':message2})
print(responseMessage2.decode("UTF-8"))