import  re
import json

class EntryAddResult():
    def __init__(self, label='', id = 0, link='', new_add=False, field='', type='', modelObj=None, *args, **kwargs):
        self.label = removeIdPrefix(label)
        self.id = id
        self.link = link
        self.new_add = new_add
        self.field = field
        self.type = type
        self.modelObj = modelObj
    def toJSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4) )  
def removeIdPrefix(inputStr:str):
    return re.sub(r'^[\d]+_', '',inputStr)