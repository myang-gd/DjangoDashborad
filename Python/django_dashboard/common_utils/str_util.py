from collections import OrderedDict 
import json
from common_utils.constant import Constant
from common_utils.json_util import JsonUtil
class StrUtil:
    
    @classmethod
    def validation_result_to_map(cls, validation_result_str):
        validation_result_map = OrderedDict()
        
        validation_result_json = JsonUtil.safe_loads(validation_result_str)
        if validation_result_json:
            for validation, result in validation_result_json.items():
                validation_str = validation
                if type(result) == type({}):
                    result_str = result[Constant.RESULT]
                    validation_str = validation + " Expected: " + result[Constant.EXPECTED] + " Actual: " + result[Constant.ACTUAL] 
                else:
                    return cls.validation_result_to_map_bysplit(validation_result_str)
                validation_result_map[validation_str] = result_str
        else:
            return cls.validation_result_to_map_bysplit(validation_result_str)
                         
        return validation_result_map
    
    @classmethod
    def validation_result_to_map_bysplit(cls, validation_result_str):
        validation_result_map = OrderedDict()
        if validation_result_str.startswith("{") : 
            validation_result_str = validation_result_str[1:]
            if validation_result_str.endswith("}") : 
                validation_result_str = validation_result_str[:-1]
    
            for validation in validation_result_str.split(","):
                validation_item = validation.split(": ")
                if len(validation_item) == 2 :
                    validation_key = validation_item[0]
                    validation_value = validation_item[1]
                elif len(validation_item) == 1 :
                    validation_key = validation_item[0]
                elif len(validation_item) > 2 :
                    validation_key = str(validation_item[0:-1])
                    validation_value = validation_item[-1]
                else:
                    validation_key = ""
                    validation_value = ""
                validation_value = validation_value.strip().strip("'")
                validation_key = validation_key.strip().strip("'")
                validation_result_map[validation_key] = validation_value
        return validation_result_map
    @staticmethod
    def str_to_bool(input_str):
        if input_str:
            return input_str.strip().lower() in ("yes", "true", "t", "1")  
        else:
            return False
    @staticmethod
    def str_none(input_obj):
        if input_obj:
            return str(input_obj)  
        else:
            return ""