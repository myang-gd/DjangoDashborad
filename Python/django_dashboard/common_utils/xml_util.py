from lxml import etree
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from enum import Enum

class AttributeType(Enum):
    
    INNER_TEXT = 1
    INNER_XML = 2
    ATR = 3
    
class ModifySetting():
    def __init__(self, attr_type, xpath, namespaces = {}, value=''):
        self.attr_type = attr_type
        self.xpath = xpath
        self.namespaces = namespaces
        self.value = value

class XmlUtil:
    
    @staticmethod
    def get_str_element(input:bytes, xpath:str, namespaces:{}) -> str:       
        result = ''
        try:
            tree = etree.fromstring(input) 
            file_refs = tree.xpath(xpath, namespaces = namespaces) 
        except:
            file_refs = []
        
        if len(file_refs) > 0 :
            result = str(file_refs.pop())

        return result
    @staticmethod
    def get_str_element_result_flag(input, xpath:str, namespaces:{}) -> str:       
        result = ''
        element_found = False
        try:
            tree = etree.fromstring(input) 
            file_refs = tree.xpath(xpath, namespaces = namespaces) 
        except:
            file_refs = []
        
        if len(file_refs) > 0 :
            result = str(file_refs.pop())
            element_found = True;

        return result, element_found
    @classmethod
    def get_elements(cls, root:ET, path:str, namespaces:{}) -> [Element]:       
        result = []
        try:
            result = root.findall(path, namespaces)
        except:
            pass
        return result
    @classmethod
    def modify_elements_from_string(cls, input:str, modify_list:[]) -> [Element]:                    
        result = ''
        try:
            root = etree.fromstring(input)
            for modify in modify_list:
                if isinstance(modify, ModifySetting): 
                    file_refs = root.xpath(modify.xpath, namespaces = modify.namespaces) 
                    if len(file_refs) > 0 :
                        node = file_refs.pop()
                        if modify.attr_type == AttributeType.INNER_TEXT:
                            node.text = modify.value
            result = etree.tostring(root).decode("utf-8") 
        
        except:
            pass
        
        return result
    
    @classmethod
    def get_key_value_list(cls, response:str) -> []:       
        result = []
        ns = {'default': 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'}
        try:
            root = ET.fromstring(response)
            parent_elemets = cls.get_elements(root, 'default:KeyValueOfstringstring', ns)
            key_value_dic = {}
            for parent_elemet in parent_elemets:
                key_text = cls.get_elements(parent_elemet, 'default:Key', ns)[0].text
                value_text = cls.get_elements(parent_elemet, 'default:Value', ns)[0].text
                key_value_dic[key_text] = value_text
                
            result.append(key_value_dic)  
        except:
            pass
        
        return result     


