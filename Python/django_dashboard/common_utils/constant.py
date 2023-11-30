from enum import Enum
class Constant:
    FAILED = 'Failed'
    PASSED = 'Passed'
    EXPECTED = 'expected'
    RESULT = 'result'
    ACTUAL = 'actual'
    QA_MONITOR_LABEL = 'qa_monitor'
    NA = 'N/A'
    ENVIRONMENT = 'Environment'
    NULL = 'NULL'
    EMPTY = 'Empty'
    NOT_EMPTY = 'NotEmpty'
    Y = 'Y'
    N = 'N'
    SUCCESS = 'success'
    ERROR = 'error'
    REQUEST = 'request'
    RESPONSE = 'response'
    HEADERS = 'headers'
    VALIDATION_RESULT= 'validationResult'
    INVALID_WSDL_URL = 'Invalid WSDL URL'
    UTF8 = 'utf-8'
    ELAPSED = 'elapsed'
    TEXT = 'text'
    
    JDBC_PROC = 'JDBC'
    CMD_PROC = 'Cmd'
    WS_PROC = 'Service_Request'
    
class ResponseType(Enum):
    key_value = 1
    json = 2
    plain = 3
    none = 0
    _KEY_VALUE, _JSON, _PLAIN = (
        '@KEY_VALUE', '@JSON', '@PLAIN'
    )
    
    TERMs = [_KEY_VALUE, _JSON, _PLAIN]
    
    @classmethod
    def toEnum(cls, input_str:str):
        if not input_str:
            return ResponseType.none
        elif cls._KEY_VALUE.value in input_str:
            return ResponseType.key_value
        elif cls._JSON.value in input_str:
            return ResponseType.json
        elif cls._PLAIN.value in input_str:
            return ResponseType.plain
        else:
            return ResponseType.none
class ValidationType(Enum):
    regex = 1
    plain = 2
    _REGEX, _PLAIN = (
        'regex', 'plain'
    )
       
    @classmethod
    def toEnum(cls, input_str:str):
        if not input_str:
            return ValidationType.plain
        elif cls._REGEX.value == input_str:
            return ValidationType.regex
        else:
            return ValidationType.plain
class OperationType(Enum):
    PTS = 1

class SOAP_VERSION(Enum):
    SOAP_1_1 = 1  
    SOAP_1_2 = 2
   
def to_enum(v,target_enum,default = None):
    '''
    if v is given enum, return it
    if v is an int, convert to enum via int convert
    if v is str convert to enum via string convert
    '''
    ret = default

    if v is None:
        return ret

    if v in target_enum:
        return v

    try:
        return target_enum(int(v))
    except Exception:
        pass

    try:
        return target_enum[str(v)]
    except Exception:
        pass

    return ret  