import json
import datetime
import objectpath
import types
import re
import itertools
from collections import OrderedDict
from jsonpath_rw_ext import parser

class JsonUtil:
    
    
    @classmethod
    def date_handler(cls, obj):
        if isinstance(obj, datetime.datetime) and hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return str(obj)
    @classmethod
    def safe_dumps(cls, toDump):       
        jason_str = ''
        try:
            jason_str = json.dumps(toDump, indent=4, sort_keys=True, default=cls.date_handler)
        except:           
            jason_str = str(toDump)
            
        return jason_str
    @staticmethod
    def safe_loads(toLoadStr):       
        json_obj = None
        try:
            json_obj = json.loads(toLoadStr)
        except:           
            pass 
            
        return json_obj
    @staticmethod
    def getActualAndExpected(validation, response_json):       
        actualList = []
        expected = "No found expected value"
        validation_new = ""
        if ":" in validation:
            validation_item = validation.split(":")
            if len(validation_item) == 2 :
                validation_new = validation_item[0].strip().strip("'").strip().strip("\"").strip()
                expected = validation_item[1].strip()
                if type(response_json) != type([]):
                    response_json = [response_json]
                for item_dic in response_json:
                    if type(item_dic) == type({}) and validation_new in item_dic:
                        actual = JsonUtil.safe_dumps(item_dic[validation_new])
                        actual = (actual.strip() if actual else actual)
                        if actual not in actualList:
                            actualList.append(actual)
                
        expected = (expected.strip() if expected else expected)   
        return actualList, expected, validation_new  
    
    @staticmethod
    def getActualAndExpectedForKeyValue(validation, response_json):       
        actualList = []
        expected = "No found expected value"
        if ":" in validation:
            validation_item = validation.split(":")
            if len(validation_item) == 2 :
                validation_new = validation_item[0].strip().strip("'").strip().strip("\"").strip()
                expected = validation_item[1].strip()
                for item_dic in response_json:
                    if type(item_dic) == type({}) and item_dic.values():
                        for dic_list in item_dic.values():
                            for key_value_dic in dic_list:
                                if validation_new in key_value_dic:                                   
                                    actual = JsonUtil.safe_dumps(key_value_dic[validation_new])
                                    actual = (actual.strip() if actual else actual)
                                    if actual not in actualList:
                                        actualList.append(actual)
        expected = (expected.strip() if expected else expected)   
        return actualList, expected, validation_new
    @staticmethod
    def get_str_element_result_flag(input_str:str, xpath:str):       
        result = ''
        element_found = False
        error = ''
        try:
            pattern = re.compile(r"(?P<node>.*)\[(?P<index>.*\d+)\].*$", re.IGNORECASE)
            match = pattern.match(xpath)
            if xpath is not None and input_str is not None and xpath.startswith('$.[') and input_str.strip().startswith('[') and input_str.strip().endswith(']'):
                xpath = xpath.replace('$.[', '$.root[') 
                input_str = '{"root":' + input_str + '}'
            if type(input_str) is OrderedDict:
                data = input_str
            else:
                data = json.loads(re.sub(r'/\*.*\*/', '', re.sub(r'\s+//.*\n', '', input_str),0, re.DOTALL | re.MULTILINE), encoding='utf8', object_pairs_hook=OrderedDict)
            if match:
                pattern_with_attr = re.compile(r"(?P<node>.*)\[(?P<index>.*\d+)\]\.(?P<attr>(\w+))$", re.IGNORECASE)
                match_with_attr = pattern_with_attr.match(xpath)
                attribute_name = None
                if match_with_attr:                    
                    node_path = match_with_attr.group('node')
                    index = match_with_attr.group('index')
                    attribute_name = match_with_attr.group('attr')                  
                else:
                    node_path = match.group('node')
                    index = match.group('index')
                                           
                jsonpath_expr = parser.ExtentedJsonPathParser().parse(node_path)
                index_find = 0
                data_found = jsonpath_expr.find(data)
                for match_find in data_found:  # dict value contained in path
                    if str(index_find) == index:
                        if not attribute_name:
                            return match_find.value,True,''
                        elif attribute_name in match_find.value:
                            return match_find.value.get(attribute_name),True,''
                    index_find += 1
                if len(data_found) == 1 and type(data_found[0].value) is list: # list value contained path
                    index_find = 0 
                    for dict_in_list in data_found[0].value:
                        if str(index_find) == index:
                            if attribute_name in dict_in_list:
                                return dict_in_list.get(attribute_name),True,''
                        index_find += 1
                        
            else:
                jsonpath_expr = parser.ExtentedJsonPathParser().parse(xpath)
                for match_find in jsonpath_expr.find(data):
                    return match_find.value,True,''
#                 tree = objectpath.Tree(data)
#                 resultList = tree.execute(xpath) # return generator
#                 if resultList is not None:
#                     if type(resultList) is types.GeneratorType or type(resultList) is itertools.chain:
#                         # dic node will be itertools.chain
#                         for item in resultList:               
#                             result = json.dumps(item)
#                             element_found = True;
#                             break;
#                     else:
#                         result = json.dumps(resultList)
#                         element_found = True;
        except Exception as e:
            error = str(e)
        
        return result, element_found, error
