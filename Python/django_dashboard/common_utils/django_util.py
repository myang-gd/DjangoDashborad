import django
from django.core.urlresolvers import reverse
class Django_Util:
    
    @classmethod
    def safe_get_object(cls, appLabel, modelName, _id):       
        _model = cls.getModel(appLabel, modelName)
        modelObj = None
        if _model:           
            if _id and _model.objects.filter(id=_id).exists():
                modelObj = _model.objects.get(id=_id)
            else:
                print('%s id = %s does not exist' % (str(modelName), _id))
        return modelObj
    @classmethod
    def getModel(cls, appLabel, modelName):
        try:
            _model = django.apps.apps.get_model(appLabel, modelName)
        except LookupError as e:
            print(e)
            return None
        else:
            return _model
    @classmethod
    def getField(cls, obj, fieldName):        
        try:
            getattr(obj, fieldName)
        except Exception as e:
            return None
        else:
            return getattr(obj, fieldName)
    @staticmethod
    def convert_to_data_provider(dic_data:{int: str}):
        if dic_data:
            return [{'label': value, 'value': key} for key, value in dic_data.items()]
        else:
            return []
    @staticmethod
    def getModelUrl(modelObj, request):
        return ''.join(['https://', request.get_host(), reverse('admin:%s_%s_change' %(modelObj._meta.app_label,  modelObj._meta.model_name),  args=[modelObj.id])])
