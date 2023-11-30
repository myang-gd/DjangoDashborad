from common_utils.ws_util import WSUtil
def getServiceResult(operation_map, service_map, endpoint, vip_name):   
        
    if operation_map['webservicetype'] == 1: # SOAP
        result = WSUtil.processSoapRequest(endpoint, operation_map['name'], service_map['port'], operation_map['requestMessage'], 
                          user=operation_map['username'], password=operation_map['password'], validations=operation_map['validations'], vip_name=vip_name)
        
    elif operation_map['webservicetype'] == 2: # REST
        result = WSUtil.processRestRequest(url=endpoint, message=service_map['requestMessage'], 
                                    validations=operation_map['validations'], headers=operation_map['headers'])
    
    return result