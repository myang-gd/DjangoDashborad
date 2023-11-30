'''
Created on Jan 25, 2016

@author: zbasmajian
'''
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_dashboard.settings')

import django
django.setup()

from apps.healthcheck.models import Environment, Vip, IndividualServer, Service, Operation,\
    WebServiceType, Team


def add_environment(name):
    environment_object = Environment.objects.get_or_create(name=name)[0]
    environment_object.name=name
    environment_object.save()
    return environment_object

def add_vip(displayName, vipName):
    vip_object = Vip.objects.get_or_create(vipName=vipName)[0]
    vip_object.displayName = displayName
    vip_object.save()
    return vip_object

def add_individualServer(name, vip, ipAddress, environment):
    individual_server_oject = IndividualServer.objects.get_or_create(name=name, vip=vip, environment=environment)[0]
    individual_server_oject.ipAddress = ipAddress
    individual_server_oject.save()
    return individual_server_oject

def add_service(name, endpoint, port):
    service_object = Service.objects.get_or_create(endpoint=endpoint, port=port)[0]
    service_object.name = name
    service_object.save()
    return service_object

def add_operation(name, requestMessage, username, password, validations, service, environment, vip, webservicetype, headers='', team=''):
    operation_object = Operation.objects.get_or_create(name=name, username=username, password=password, service=service, environment=environment, 
                                                       vip=vip, webservicetype=webservicetype, team=team)[0]
    operation_object.name = name
    operation_object.requestMessage = requestMessage
    operation_object.headers = headers
    operation_object.team = team
    operation_object.validations = validations
    operation_object.save()
    return operation_object

def add_webservicetype(name):
    webservicetype_object = WebServiceType.objects.get_or_create(name=name)[0]
    webservicetype_object.name = name
    webservicetype_object.save()
    return webservicetype_object

def add_team(name, email):
    team_object = Team.objects.get_or_create(name=name)[0]
    team_object.email = email
    team_object.save()
    return team_object



def populate():
    
    '''Adding Teams'''
    platform_team= add_team(name="Platform", email="Platform-QA-All@greendotcorp.com", jiraTeamName="Platform")
    walmart_team= add_team(name="Walmart", email="WalmartITCoreQA@greendotcorp.com", jiraTeamName="Walmart")
    greendot_team= add_team(name="GreenDot", email="IT-GD-QA-Team@greendotcorp.com", jiraTeamName="Green Dot")
    gdn_team= add_team(name="GDN", email="GDN-QA@greendotcorp.com", jiraTeamName="GDN")
    risk_team= add_team(name="Risk", email="RISKQA@greendotcorp.com", jiraTeamName="Risk")
    processor_team = add_team(name="Processor", email="ProcessingQA@greendotcorp.com", jiraTeamName="Processing")
    gobank_team = add_team(name="GoBank", email="GoBank_QA@greendotcorp.com", jiraTeamName="Go Bank")
    
    '''Adding Web Service Type'''
    soap_type = add_webservicetype(name='SOAP')
    rest_type = add_webservicetype(name='REST')
    
    '''Adding Environment'''
    devint1_environment = add_environment(name="DevInt1")
    devint2_environment = add_environment(name="DevInt2")
    qa3_environment = add_environment(name="QA3")
    qa4_environment = add_environment(name="QA4")
    qa5_environment = add_environment(name="QA5")
    production_environment = add_environment(name="Production")
    
    '''Adding Vips'''
    com_vip = add_vip(displayName='COM',vipName='necla')
    soacom_vip = add_vip(displayName='SOACOM',vipName='gdcsvc')
    v3_vip = add_vip(displayName='V3', vipName='gdcsvcv3')
    partner_greendotcorp_vip = add_vip(displayName='partners', vipName='partners.greendotcorp.com')
    
    '''Adding DevInt1 individual Servers'''
    add_individualServer(name='GDCDI1COM201', vip=com_vip, ipAddress='10.10.38.146', environment=devint1_environment)
    add_individualServer(name='GDCDEVISOACOM01', vip=soacom_vip, ipAddress='10.50.4.214', environment=devint1_environment)
    add_individualServer(name='GDCDI1V3SVC21', vip=v3_vip, ipAddress='10.10.38.48', environment=devint1_environment)
    add_individualServer(name='di1-partners.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='di1-partners.greendotcorp.com', environment=devint1_environment)
    
    
    '''DevInt2 individual Servers'''
    add_individualServer(name='GDCDI2COM201', vip=com_vip, ipAddress='10.50.5.198', environment=devint2_environment)
    add_individualServer(name='GDCDI2-SOACOM01', vip=soacom_vip, ipAddress='10.50.55.132', environment=devint2_environment)
    add_individualServer(name='GDCDI2V3SVC21', vip=v3_vip, ipAddress='10.10.38.47', environment=devint2_environment)
    add_individualServer(name='dev-partners.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='dev-partners.greendotcorp.com', environment=devint2_environment)
    

    '''Adding QA3 Individual Servers'''
    add_individualServer(name='GDCQA3COM201', vip=com_vip, ipAddress='10.10.38.174', environment=qa3_environment)
    add_individualServer(name='GDCQA3-SOACOM01', vip=soacom_vip, ipAddress='10.50.55.36', environment=qa3_environment)
    add_individualServer(name='GDCQA3V3SVC21', vip=v3_vip, ipAddress='10.10.38.52', environment=qa3_environment)    
    add_individualServer(name='qa3-partners.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='qa3-partners.greendotcorp.com', environment=qa3_environment)

    
    '''Adding QA4 Individual Servers'''
    add_individualServer(name='GDCQA4COM201', vip=com_vip, ipAddress='10.10.38.166', environment=qa4_environment)
    add_individualServer(name='GDCQA4-SOACOM01', vip=soacom_vip, ipAddress='10.50.55.37', environment=qa4_environment)
    add_individualServer(name='GDCQA4V3SVC21', vip=v3_vip, ipAddress='10.10.38.51', environment=qa4_environment)   
    add_individualServer(name='qa4-partners.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='qa4-partners.greendotcorp.com', environment=qa4_environment)

    
    '''Adding QA5 Individual Servers'''
    #COM
    add_individualServer(name='GDCQA5COM201', vip=com_vip, ipAddress='10.10.38.155', environment=qa5_environment)
    add_individualServer(name='GDCQA5COM202', vip=com_vip, ipAddress='10.10.38.156', environment=qa5_environment)
    #SOACOM
    add_individualServer(name='GDCQA5-SOACOM01', vip=soacom_vip, ipAddress='10.50.55.38', environment=qa5_environment)
    add_individualServer(name='GDCQA5-SOACOM02', vip=soacom_vip, ipAddress='10.50.55.64', environment=qa5_environment)
    #V3
    add_individualServer(name='GDCQA5V3SVC21', vip=v3_vip, ipAddress='10.10.38.49', environment=qa5_environment)
    add_individualServer(name='GDCQA5V3SVC22', vip=v3_vip, ipAddress='10.10.38.50', environment=qa5_environment)
    add_individualServer(name='qa5-partners.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='qa5-partners.greendotcorp.com', environment=qa5_environment)
   
    '''Adding Production Individual Servers'''
    #COM
    add_individualServer(name='DC1COM201', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM202', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM203', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM204', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM205', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM206', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM207', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COM208', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COMRETAIL201', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1COMRETAIL202', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM201', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM202', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM203', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM204', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM205', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM206', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM207', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COM208', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COMRETAIL201', vip=com_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2COMRETAIL202', vip=com_vip, ipAddress='N/A', environment=production_environment)
    
    #SOACOM
    add_individualServer(name='DC1SOACOM01', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM02', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM03', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM04', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM05', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM06', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM07', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOM08', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1SOACOMGB04', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM01', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM02', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM03', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM04', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM05', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM06', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM07', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOM08', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOMGB03', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2SOACOMGB04', vip=soacom_vip, ipAddress='N/A', environment=production_environment)
             
    #V3
    add_individualServer(name='DC1V3SVC01', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1V3SVC02', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1V3SVC03', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC1V3SVC04', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2V3SVC01', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2V3SVC02', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2V3SVC03', vip=v3_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='DC2V3SVC04', vip=v3_vip, ipAddress='N/A', environment=production_environment)
  
    #PARTNERS SERVICE
    add_individualServer(name='partners-s1.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='partners-s2.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='partners-s3.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='N/A', environment=production_environment)
    add_individualServer(name='partners-s4.greendotcorp.com', vip=partner_greendotcorp_vip, ipAddress='N/A', environment=production_environment)


  
    '''Adding Services'''
    # V3 Services
    product_v3_service = add_service(name='Product V3 Service', endpoint='http://gdcsvcv3/Product/Product.svc?wsdl', port='ProductService.Product.Endpoint')
    accountmanagement_v3_service = add_service(name='AccountManagement V3 Service', endpoint='http://gdcsvcv3/AccountManagement/AccountManagement.svc?wsdl', port='AccountManagement.IAccountManagement.Endpoint')
    
    #Legacy Services
    transaction_legacy_service = add_service(name='Transaction Legacy Service', endpoint='http://necla/NECWS_TransactionAPI/TransactionService.asmx?wsdl', port='TransactionServiceSoap12')
    product_legacy_service = add_service(name='Product Legacy Service', endpoint='http://necla/Corporate/GDCWS_Product/ProductService.svc?wsdl', port='BasicHttpBinding_IProduct')
    
    #SOA Services
    bank_soa_service = add_service(name='Bank SOA Service', endpoint='http://gdcsvc/Entity/Bank/BankService?wsdl', port='BasicHttpBinding_IBank')
    remotedeposit_soa_service = add_service(name='RemoteDeposit SOA Service', endpoint='http://gdcsvc/Composite/RemoteDeposit/RemoteDepositService?wsdl', port='BasicHttpBinding_IRemoteDeposit')
    
    # REST Service (GDN Disbursement)
    disbursement_rest_v1_service = add_service(name='Disbursement REST V1 Service', endpoint='https://partners.greendotcorp.com/Disbursements/api/v1/', port='')
   
    
    ''' Adding Operations '''
    add_operation(name='GetProduct', requestMessage="""<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:ns1="http://Product.GreendotCorp.com/Product" 
                                        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" 
                                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">
                                        <SOAP-ENV:Header/><ns0:Body><ns1:GetProduct><ns1:request><ns2:ProductCode>1424</ns2:ProductCode><ns2:ProductKey xsi:nil="true"/>
                                        <ns2:ProductName xsi:nil="true"/></ns1:request></ns1:GetProduct></ns0:Body></SOAP-ENV:Envelope>""", 
                                        username='nextestate\svc_QA_V3Test', password='Greendot1', validations='PostalCode = "84604", Name = "Green Dot Bank"',
                                         service=product_v3_service, environment=qa4_environment, vip=v3_vip, webservicetype=soap_type, team=platform_team)

    add_operation(name='GetFees', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prod="http://Product.GreendotCorp.com/Product"><soapenv:Header/>
                                    <soapenv:Body> <prod:GetFees><prod:request> <gdot:ProductKey xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">2181</gdot:ProductKey>
                                    </prod:request></prod:GetFees></soapenv:Body></soapenv:Envelope>""", 
                                    username='nextestate\svc_QA_V3Test', password='Greendot1', validations='ResponseCode = "Success"', service=product_v3_service, 
                                    environment=qa4_environment, vip=v3_vip, webservicetype=soap_type, team=platform_team)

    add_operation(name='GetAccountInfo', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:acc="http://AccountManagement.GreendotCorp.com/AccountManagement">
                                            <soapenv:Header/><soapenv:Body><acc:GetAccountInfo><acc:request><gdot:UserToken xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.AccountManagement.Contract.DataContract.Request">10</gdot:UserToken>
                                            <gdot:AccountKey xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.AccountManagement.Contract.DataContract.Request">4037541</gdot:AccountKey>
                                            <gdot:AdditionalEntities xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.AccountManagement.Contract.DataContract.Request">None</gdot:AdditionalEntities>
                                            <gdot:IsUpToDateBalanceNeeded xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.AccountManagement.Contract.DataContract.Request">false</gdot:IsUpToDateBalanceNeeded>
                                            </acc:request></acc:GetAccountInfo></soapenv:Body></soapenv:Envelope>""", 
                                        username='nextestate\svc_QA_V3Test', password='Greendot1', validations='ResponseCode = "AmSuccess", ProductKey = "6666"', 
                                        service=accountmanagement_v3_service, environment=qa4_environment, vip=v3_vip, webservicetype=soap_type, team=platform_team)
    
    add_operation(name='Customers', requestMessage="""customers/vv1234""", username='', password='', validations='responsemessage = Success', 
                                    service=disbursement_rest_v1_service, environment=qa4_environment, vip=partner_greendotcorp_vip, webservicetype=rest_type, 
                                    headers="""Authorization = Basic Z2RjcGZuZHVzZXI6SC9sVFBpa0ZNSGtHekdNQW9uOHQ2Y1JxZEdNPQ==, 
                                               endusersecurityid = 1234_Test,
                                               requestid = 20194767388632,
                                               partneridentifier = GDCPreFund,
                                               enduserip = 10.23.21.21
                                            """, team=gdn_team) 
    
    add_operation(name='GetBank', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://greendotcorp.com/services/entity/Bank/v1">
                                                   <soapenv:Header>
                                                      <X-GDC-ApplicationID>8017</X-GDC-ApplicationID>
                                                   </soapenv:Header>
                                                   <soapenv:Body>
                                                      <v1:GetBank>
                                                         <v1:request>
                                                            <gdot:BankToken xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Entity.Bank.Contract.DataContract">3</gdot:BankToken>
                                                         </v1:request>
                                                      </v1:GetBank>
                                                   </soapenv:Body>
                                                </soapenv:Envelope>""", username='', password='', validations='TotalCount = "1", Name = "Green Dot Bank"', 
                                                service=bank_soa_service, environment=qa4_environment, vip=soacom_vip, webservicetype=soap_type, team=platform_team)
    
    
    add_operation(name='GetProduct', requestMessage="""<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:ns1="http://Product.GreendotCorp.com/Product" 
                                        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" 
                                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">
                                        <SOAP-ENV:Header/><ns0:Body><ns1:GetProduct><ns1:request><ns2:ProductCode>1424</ns2:ProductCode><ns2:ProductKey xsi:nil="true"/>
                                        <ns2:ProductName xsi:nil="true"/></ns1:request></ns1:GetProduct></ns0:Body></SOAP-ENV:Envelope>""", 
                                        username='nextestate\svc_QA_V3Test', password='Greendot1', validations='PostalCode = "84604", Name = "Green Dot Bank"', 
                                        service=product_v3_service, environment=qa5_environment,  vip=v3_vip, webservicetype=soap_type, team=platform_team)

    add_operation(name='GetFees', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prod="http://Product.GreendotCorp.com/Product"><soapenv:Header/>
                                    <soapenv:Body> <prod:GetFees><prod:request> <gdot:ProductKey xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">2181</gdot:ProductKey>
                                    </prod:request></prod:GetFees></soapenv:Body></soapenv:Envelope>""", 
                                    username='nextestate\svc_QA_V3Test', password='Greendot1', validations='ResponseCode = "Success"', 
                                    service=product_v3_service, environment=qa5_environment, vip=v3_vip, webservicetype=soap_type, team=platform_team)
    
    add_operation(name='GetBank', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://greendotcorp.com/services/entity/Bank/v1">
                                                   <soapenv:Header>
                                                      <X-GDC-ApplicationID>8017</X-GDC-ApplicationID>
                                                   </soapenv:Header>
                                                   <soapenv:Body>
                                                      <v1:GetBank>
                                                         <v1:request>
                                                            <gdot:BankToken xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Entity.Bank.Contract.DataContract">3</gdot:BankToken>
                                                         </v1:request>
                                                      </v1:GetBank>
                                                   </soapenv:Body>
                                                </soapenv:Envelope>""", username='', password='', validations='TotalCount = "1", Name = "Green Dot Bank"', 
                                                service=bank_soa_service, environment=qa5_environment, vip=soacom_vip, webservicetype=soap_type, team=platform_team)    
        
    add_operation(name='GetProduct', requestMessage="""<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:ns1="http://Product.GreendotCorp.com/Product" 
                                        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" 
                                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">
                                        <SOAP-ENV:Header/><ns0:Body><ns1:GetProduct><ns1:request><ns2:ProductCode>1424</ns2:ProductCode><ns2:ProductKey xsi:nil="true"/>
                                        <ns2:ProductName xsi:nil="true"/></ns1:request></ns1:GetProduct></ns0:Body></SOAP-ENV:Envelope>""", 
                                        username='nextestate\svc_QA_V3Test', password='Greendot1', validations='PostalCode = "84604", Name = "Green Dot Bank"', 
                                        service=product_v3_service, environment=qa3_environment, vip=v3_vip,  webservicetype=soap_type, team=platform_team)

    add_operation(name='GetFees', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:prod="http://Product.GreendotCorp.com/Product"><soapenv:Header/>
                                    <soapenv:Body> <prod:GetFees><prod:request> <gdot:ProductKey xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Product.Contract.DataContract.Request">2181</gdot:ProductKey>
                                    </prod:request></prod:GetFees></soapenv:Body></soapenv:Envelope>""", 
                                    username='nextestate\svc_QA_V3Test', password='Greendot1', validations='ResponseCode = "Success"', 
                                    service=product_v3_service, environment=qa3_environment, vip=v3_vip, webservicetype=soap_type, team=platform_team)
    
    add_operation(name='GetBank', requestMessage="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://greendotcorp.com/services/entity/Bank/v1">
                                                   <soapenv:Header><X-GDC-ApplicationID>8017</X-GDC-ApplicationID></soapenv:Header><soapenv:Body><v1:GetBank><v1:request>
                                                   <gdot:BankToken xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.Entity.Bank.Contract.DataContract">3</gdot:BankToken>
                                                   </v1:request></v1:GetBank> </soapenv:Body> </soapenv:Envelope>""", 
                                                   username='', password='', validations='TotalCount = "1", Name = "Green Dot Bank"', 
                                                   service=bank_soa_service, environment=qa3_environment, vip=soacom_vip, webservicetype=soap_type, team=platform_team)
    

if __name__ == '__main__':
    print ("Starting Healthcheck population script...")
    populate()
    print ("Done!!")