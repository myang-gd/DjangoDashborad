import threading
from apps.qa_monitor.models import MonitorType
class Config:
    
    __singleton_lock = threading.Lock()
    __singleton_instance = None
    
    SERVER = 'server'
    DB = 'db'
    USER = 'user'
    PWD = 'pwd'
    MESSAGE = 'message'
    URL = 'url'
    METHOD = 'method'
    PORT = 'port'
    VALIDATIONS = 'validations'
    
    data = {}    
    def __init__(self):
        self.data = DataFeed.get_operation_dic()    

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance
    @classmethod
    def getMonitorConfig(cls, monitor_type, environment):
        result_dic = {}
        config = Config.instance()
        if monitor_type in config.data.keys():
            if environment in config.data.get(monitor_type).keys():
                result_dic =  config.data.get(monitor_type).get(environment)   
        return  result_dic  
class DataFeed:
     
    @staticmethod
    def get_operation_dic():
        # TSYS
        Operations_environment_map = {}
        TSYS_QUEUE_QUERY = '''SELECT count(*) as MessageCount FROM TSYSQueue
                                WHERE ResponseDate IS NULL
                                AND TSYSResponseCodeKey IS NULL
                                AND ProductKey IN (SELECT ProductKey FROM Product
                                WHERE ProductSourceKey = 99)'''
        TsysDBs = {}
        TsysDBs['QA3'] = {Config.SERVER: 'GDCQA3SQL01', Config.DB:'NEC', Config.USER:'qa_automation', Config.PWD :'Gr33nDot!' , Config.MESSAGE:TSYS_QUEUE_QUERY}
        TsysDBs['QA4'] = {Config.SERVER: 'GDCQA4-SQL01', Config.DB:'NEC', Config.USER:'qa_automation', Config.PWD :'Gr33nDot!' , Config.MESSAGE:TSYS_QUEUE_QUERY}
        TsysDBs['QA5'] = {Config.SERVER: 'GDCQA5VSQL01', Config.DB:'NEC', Config.USER:'qa_automation', Config.PWD :'Gr33nDot!' , Config.MESSAGE:TSYS_QUEUE_QUERY}
        TsysDBs['DevInt1'] = {Config.SERVER: 'GDCDEV3-SQL1', Config.DB:'INTEGRATION', Config.USER:'sqlquery', Config.PWD :'AdHoc705' , Config.MESSAGE:TSYS_QUEUE_QUERY}
        TsysDBs['DevInt2'] = {Config.SERVER: 'GDCDI2-SQL01', Config.DB:'Integration2', Config.USER:'sqlquery', Config.PWD :'AdHoc705' , Config.MESSAGE:TSYS_QUEUE_QUERY}
        Operations_environment_map[MonitorType.TSYS_QUEUE] = TsysDBs
        
        #GetPin
        GetPinOperations = {}
        pin_grabber_request_QA4 = '''<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:gdqa="http://GDQA_CentralTestEngine.com">
                                       <soapenv:Header><X-GDC-ApplicationID>8017</X-GDC-ApplicationID></soapenv:Header>
                                       <soapenv:Body>
                                          <gdqa:GetPin>
                                             <gdqa:request>
                                                <gdqa:PinGrabRequest>
                                                   <gdqa:Environment>QA4</gdqa:Environment>
                                                   <gdqa:IsReload>false</gdqa:IsReload>
                                                   <gdqa:LoadAmount>0</gdqa:LoadAmount>
                                                   
                                                   <gdqa:ProductCode>-1234</gdqa:ProductCode>
                                                </gdqa:PinGrabRequest>
                                             </gdqa:request>
                                          </gdqa:GetPin>
                                       </soapenv:Body>
                                    </soapenv:Envelope>'''
        GetPinOperations['QA3'] = {Config.URL: 'http://10.10.38.174/GDQA_Tools/GDQA_CentralTestEngine/GDQA_CentralTestEngine/CentralTestEngine.svc?singleWsdl', 
                                        Config.METHOD:'GetPin', Config.PORT:'BasicHttpBinding_ICentralTestEngine', 
                                        Config.MESSAGE :pin_grabber_request_QA4 , Config.VALIDATIONS:'<Exceptions i:nil="true"/>'}
        GetPinOperations['QA4'] = {Config.URL: 'http://10.10.38.166/GDQA_Tools/GDQA_CentralTestEngine/GDQA_CentralTestEngine/CentralTestEngine.svc?singleWsdl', 
                                        Config.METHOD:'GetPin', Config.PORT:'BasicHttpBinding_ICentralTestEngine', 
                                        Config.MESSAGE :pin_grabber_request_QA4 , Config.VALIDATIONS:'<Exceptions i:nil="true"/>'}
        GetPinOperations['QA5'] = {Config.URL: 'http://10.10.38.155/GDQA_Tools/GDQA_CentralTestEngine/GDQA_CentralTestEngine/CentralTestEngine.svc?singleWsdl', 
                                        Config.METHOD:'GetPin', Config.PORT:'BasicHttpBinding_ICentralTestEngine', 
                                        Config.MESSAGE :pin_grabber_request_QA4 , Config.VALIDATIONS:'<Exceptions i:nil="true"/>'}
        GetPinOperations['DevInt1'] = {Config.URL: 'http://10.10.38.146/GDQA_Tools/GDQA_CentralTestEngine/GDQA_CentralTestEngine/CentralTestEngine.svc?singleWsdl', 
                                        Config.METHOD:'GetPin', Config.PORT:'BasicHttpBinding_ICentralTestEngine', 
                                        Config.MESSAGE :pin_grabber_request_QA4 , Config.VALIDATIONS:'<Exceptions i:nil="true"/>'}
        GetPinOperations['DevInt2'] = {Config.URL: 'http://10.50.5.198/GDQA_Tools/GDQA_CentralTestEngine/GDQA_CentralTestEngine/CentralTestEngine.svc?singleWsdl', 
                                        Config.METHOD:'GetPin', Config.PORT:'BasicHttpBinding_ICentralTestEngine', 
                                        Config.MESSAGE :pin_grabber_request_QA4 , Config.VALIDATIONS:'<Exceptions i:nil="true"/>'}
        Operations_environment_map[MonitorType.PIN_GRABBER] = GetPinOperations
        
        #GetPAL
        pal_request_QA3 = '''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:v1="http://greendotcorp.com/processor/service/v1" xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.ProcessorTransmission.Contract.Message" xmlns:gdot1="http://schemas.datacontract.org/2004/07/Gdot.Core.Types" xmlns:v11="http://greendotcorp.com/processor/entity/balance/message/v1" xmlns:v12="http://greendotcorp.com/shared/data/v1">
                                <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing"><wsa:Action>http://greendotcorp.com/processor/service/v1/IProcessorTransmission/GetAccountDetails</wsa:Action><wsa:To>http://gdcqa4ipscom01/ProcessorTransmission/ProcessorTransmission.svc</wsa:To></soap:Header>
                                <soap:Body>
                                   <v1:GetAccountDetails>
                                      <v1:request>
                                         <gdot:CallChainID>
                                            <gdot1:value>3a5a1309-ded2-433e-964a-6b763de70fe1</gdot1:value>
                                         </gdot:CallChainID>
                                         <v11:AccountReferenceID>
                                            <v12:Value>A1F2F5D3-2018-E611-940D-005056B53CD8</v12:Value>
                                         </v11:AccountReferenceID>
                                       </v1:request>
                                   </v1:GetAccountDetails>
                                </soap:Body>
                             </soap:Envelope>'''
        pal_request_QA4 = '''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:v1="http://greendotcorp.com/processor/service/v1" xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.ProcessorTransmission.Contract.Message" xmlns:gdot1="http://schemas.datacontract.org/2004/07/Gdot.Core.Types" xmlns:v11="http://greendotcorp.com/processor/entity/balance/message/v1" xmlns:v12="http://greendotcorp.com/shared/data/v1">
                                <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing"><wsa:Action>http://greendotcorp.com/processor/service/v1/IProcessorTransmission/GetAccountDetails</wsa:Action><wsa:To>http://gdcqa4ipscom01/ProcessorTransmission/ProcessorTransmission.svc</wsa:To></soap:Header>
                                <soap:Body>
                                   <v1:GetAccountDetails>
                                      <v1:request>
                                         <gdot:CallChainID>
                                            <gdot1:value>3a5a1309-ded2-433e-964a-6b763de70fe1</gdot1:value>
                                         </gdot:CallChainID>
                                         <v11:AccountReferenceID>
                                            <v12:Value>0170BB73-2317-E611-940F-944B693B3A6A</v12:Value>
                                         </v11:AccountReferenceID>
                                       </v1:request>
                                   </v1:GetAccountDetails>
                                </soap:Body>
                             </soap:Envelope>'''
        pal_request_QA5 = '''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:v1="http://greendotcorp.com/processor/service/v1" xmlns:gdot="http://schemas.datacontract.org/2004/07/Gdot.ProcessorTransmission.Contract.Message" xmlns:gdot1="http://schemas.datacontract.org/2004/07/Gdot.Core.Types" xmlns:v11="http://greendotcorp.com/processor/entity/balance/message/v1" xmlns:v12="http://greendotcorp.com/shared/data/v1">
                                <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing"><wsa:Action>http://greendotcorp.com/processor/service/v1/IProcessorTransmission/GetAccountDetails</wsa:Action><wsa:To>http://gdcqa4ipscom01/ProcessorTransmission/ProcessorTransmission.svc</wsa:To></soap:Header>
                                <soap:Body>
                                   <v1:GetAccountDetails>
                                      <v1:request>
                                         <gdot:CallChainID>
                                            <gdot1:value>3a5a1309-ded2-433e-964a-6b763de70fe1</gdot1:value>
                                         </gdot:CallChainID>
                                         <v11:AccountReferenceID>
                                            <v12:Value>92837F37-121C-E611-9420-005056B50EE2</v12:Value>
                                         </v11:AccountReferenceID>
                                       </v1:request>
                                   </v1:GetAccountDetails>
                                </soap:Body>
                             </soap:Envelope>'''
        GetPALOperations = {}
        GetPALOperations['QA3'] = {Config.URL: 'http://10.10.38.78/ProcessorTransmission/ProcessorTransmission.svc?wsdl', 
                                        Config.METHOD:'GetAccountDetails', Config.PORT:'ProcessorTransmission.WsHttpEndPoint', 
                                        Config.MESSAGE :pal_request_QA3 , Config.VALIDATIONS:'''<Success xmlns="http://schemas.datacontract.org/2004/07/Gdot.ProcessorTransmission.Contract.Message">true</Success>'''}
        GetPALOperations['QA4'] = {Config.URL: 'http://10.10.38.100/ProcessorTransmission/ProcessorTransmission.svc?wsdl', 
                                        Config.METHOD:'GetAccountDetails', Config.PORT:'ProcessorTransmission.WsHttpEndPoint', 
                                        Config.MESSAGE :pal_request_QA4 , Config.VALIDATIONS:'''<Success xmlns="http://schemas.datacontract.org/2004/07/Gdot.ProcessorTransmission.Contract.Message">true</Success>'''}
        GetPALOperations['QA5'] = {Config.URL: 'http://10.10.38.90/ProcessorTransmission/ProcessorTransmission.svc?wsdl', 
                                        Config.METHOD:'GetAccountDetails', Config.PORT:'ProcessorTransmission.WsHttpEndPoint', 
                                        Config.MESSAGE :pal_request_QA5 , Config.VALIDATIONS:'''<Success xmlns="http://schemas.datacontract.org/2004/07/Gdot.ProcessorTransmission.Contract.Message">true</Success>'''}
        Operations_environment_map[MonitorType.PAL] = GetPALOperations
        
        return Operations_environment_map
        