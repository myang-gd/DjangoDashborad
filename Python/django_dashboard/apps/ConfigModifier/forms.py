from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from .models import Servers,Fields
from enum import Enum
from . import models

def validate_path(value):
    pattern = re.compile(r'(?P<driver>^[a-zA-Z]:\\?)(?P<middle>([^\\]+\\)*)(?P<file>([^\\])+$)')
    match = pattern.match(value)    
    if not match:
        raise ValidationError(
            _(r'%(value)s is not an valid path'),
            params={'value': value},
        )
 
def validate_share_path(value):
    pattern = re.compile(r"(?P<server>^\\\\(?<!-)[a-z0-9-.]{1,100}(?!-)\\?)(?P<middle>([^\\]+\\)+)(?P<file>([^\\])+$)",re.IGNORECASE)
    match = pattern.match(value)    
    if not match:
        raise ValidationError(
            _(r'%(value)s is not an valid path'),
            params={'value': value},
        )
    else:
        server = match.group('server').replace('\\','').strip()
        if not Servers.objects.filter(server_name=server).exists():
            raise ValidationError(
                _('Server: %(value)s does not exist in DB'),
                params={'value': server},
            )

def validate_key_value(value):
    pattern = re.compile('^(.+=".+")(\r\n.+=".+")*$')
    match = pattern.match(value)    
    if not match:
        raise ValidationError(
            _('%(value)s is not an valid format e.g. key1="value1" (line break) key2="value2"'),
            params={'value': value},
        )        
def validate_field(value):
    if not Fields.objects.filter(id=value).exists():
        raise ValidationError(
                _('Field: id=%(id)s does not exist in DB'),
                params={'id': str(value)},
            )

def getFieldParaMap(fieldParas:str)-> {}:
    return_map = {}
    for para in fieldParas.split('\r\n'):
        pattern = re.compile(r'(?P<key>.+)=\"(?P<value>.+)\"$')
        match = pattern.match(para) 
        if match:
            return_map[match.group('key')] = match.group('value')
            
    return return_map

class EntryForm(forms.Form):
    
    def __init__(self, node_type='', value_count = 2, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.applyNodeType(node_type)
        self.applyValueCount(value_count)
        
    def applyValueCount(self, value_count=2):
        i = 1
        while(i <= value_count):
            self.fields['field_value-' + str(i)] = forms.CharField(label=('Attribute value - %s' % str(i) ), widget=forms.Textarea(attrs={'placeholder': ('value%s'  % str(i))}), help_text='The valid value of node attribute, optional e.g. value1' , required=False)
            i = i + 1
            
    def applyNodeType(self, node_type=''):
        if node_type:
            if node_type== '1':
                self.fields['parent_id'].widget = forms.HiddenInput()
                self.fields['remove_field'].widget = forms.HiddenInput()
                self.fields['remove_attribute'].widget = forms.HiddenInput()
            elif node_type== '2':
                self.fields['parent_id'].widget = forms.HiddenInput()
                self.fields['remove_field'].widget = forms.HiddenInput()
                self.fields['remove_attribute'].initial = True
            elif node_type== '3':
                self.fields['parent_id'].widget = forms.HiddenInput()
                self.fields['remove_attribute'].widget = forms.HiddenInput()
                self.fields['remove_field'].initial = True
    ELEMENT_PATH,ATTRIBUTE,PARENT_ID,FIELD_PARAMS,FIELD_VALUES,NAMESPACE,REMOVE_FIELD,REMOVE_ATTRIBUTE=('element_path','attribute','parent_id','field_params',
                                                                                                        'field_values','namespace','remove_field','remove_attribute')  
    VALUE_COUNT = "value_count"
    
    element_path = forms.CharField(label='Node path', max_length=200, help_text='Name of the node you want to add/modify e.g. add', widget=forms.TextInput(attrs={'placeholder': 'add'}))
    attribute = forms.CharField(label='Node Attribute', max_length=200, help_text='Attribute of the node you want to change e.g. value, InnerText', required=False, widget=forms.TextInput(attrs={'placeholder': 'value'}))
    parent_id = forms.IntegerField(label='Parent node id',  help_text='The id of the parent node e.g. 1239', required=False, widget=forms.TextInput(attrs={'placeholder': '1239'},), validators=[validate_field])
    field_params = forms.CharField(label='Search Attributes', widget=forms.Textarea(attrs={'placeholder': 'key="SFMCMigrationDisabled"'}), help_text='The unique attribute to identify expected node e.g. e.g. key1:value1 (line break) key2:value2', validators=[], required=False)
    namespace = forms.CharField(label='Node Namespace', max_length=250, widget=forms.TextInput(attrs={'placeholder': 'http://www.nlog-project.org/schemas/NLog.xsd'}), help_text='e.g. name space for the node' , required=False)
    remove_field = forms.BooleanField(label='Is new field ?', required=False)
    remove_attribute = forms.BooleanField(label='Is new attribute ?', required=False)
    
    def clean(self):
        cleaned_data = super(EntryForm, self).clean()
        field_params = cleaned_data.get(self.FIELD_PARAMS,"")
        attribute = cleaned_data.get(self.ATTRIBUTE,"")
        if attribute and attribute in getFieldParaMap(field_params):
            raise forms.ValidationError(
                "Search attributes can't contain node attribute."
            )

class EntryCommonForm(forms.Form):
    SHARE_PATH,NEED_VALIDATE=('share_path','need_validate')
    share_path = forms.CharField(label='Share path', max_length=200,widget=forms.TextInput(attrs={'placeholder': r'\\GDCQA4V3SVC21\GDCWeb\Notification\Web.config'}),help_text=r'e.g. \\GDCQA4APP201\GDCWeb\Notification\Web.config', validators=[validate_share_path])
    need_validate = forms.BooleanField(required=False, initial=True, help_text=r'Need to validate whether can access the share path and find the field base on path/attribute?')
    
class EntrySelectForm(forms.Form):
    def __init__(self,*args, **kwargs):
        request = kwargs.pop('request', None)
        super(EntrySelectForm, self).__init__(*args, **kwargs)
        CHOICES = ()
        if request:
            user = request.user
            can_add_modify_attr = user.has_perm('ConfigModifier.add_fields_modify_attr')
            can_add_new_attr = user.has_perm('ConfigModifier.add_fields_new_attr')
#             can_add_new_node = user.has_perm('ConfigModifier.add_fields_new_node')
            can_add_adv_node = user.has_perm('ConfigModifier.add_fields_adv')
            choice_list = []
            if can_add_modify_attr:
                choice_list.append( ('1', 'Add new attribute value'))
#             if can_add_new_attr:
#                 choice_list.append( ('2', 'Add new attribute'))
#             if can_add_new_node:
#                 choice_list.append( ('3', 'Add new node'))
            if can_add_adv_node:
                choice_list.append( ('4', 'Advanced adding'))
            if choice_list:
                CHOICES = tuple(choice_list)
            else:
                CHOICES = ()
            self.fields['node_type'].widget = forms.Select(choices=CHOICES)   

    NODE_TYPE = 'node_type'
    node_type = forms.CharField(widget=forms.Select(choices=()), help_text='Please select the type of node', max_length=100)
    
class MRTFormType(Enum):
    NORMAL = 1
    ADDFEATURE= 2
    
class Choices():
    def __init__(self, choices, initial=''):
        self.choices = choices
        self.initial = initial
        
def reBuildChoiceWidget(choiceObj, field, is_multi=False):  
    if choiceObj and field:
        if choiceObj.choices:
            if is_multi:
                field.widget = forms.SelectMultiple(choices=choiceObj.choices)
            else:
                field.widget = forms.Select(choices=choiceObj.choices)
        else:
            field.widget = forms.Select(choices=()) 
        if choiceObj.initial:
            field.initial = choiceObj.initial
class MakeRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        environment_choices = kwargs.pop('environment_choices', None)
        st_choices = kwargs.pop('st_choices', None)
        ftype = kwargs.pop('ftype', None)
        server_choices = kwargs.pop('server_choices', None)
        file_choices = kwargs.pop('file_choices', None)
        config_choices = kwargs.pop('config_choices', None)
        feature_name = kwargs.pop('feature_name', None)
        ignore_server = kwargs.pop('ignore_server', None)
        value_type_choices = kwargs.pop('value_type_choices', None)
        
        super(MakeRequestForm, self).__init__(*args, **kwargs) 
              
        if environment_choices:
            reBuildChoiceWidget(environment_choices, self.fields['environment'] )
        if st_choices:
            reBuildChoiceWidget(st_choices, self.fields['server_type'] )
        if server_choices:
            reBuildChoiceWidget(server_choices, self.fields['server'] )        
        if file_choices:
            reBuildChoiceWidget(file_choices, self.fields['file'] )        
        if config_choices:
            reBuildChoiceWidget(config_choices, self.fields['config'] )
        if value_type_choices:
            reBuildChoiceWidget(value_type_choices, self.fields['value_type'] )
            
        if ftype == MRTFormType.ADDFEATURE:
            self.fields['field_value'].widget = forms.HiddenInput()
            self.fields['timer'].widget = forms.HiddenInput()
            self.fields['field_value_list'].widget = forms.HiddenInput()
            self.fields['include_all_servers'].widget = forms.HiddenInput()
        else:
            self.fields['feature_name'].widget = forms.HiddenInput()
            self.fields['ignore_server'].widget = forms.HiddenInput()
        if feature_name:
            self.fields['feature_name'].initial = feature_name 
        if ignore_server is not None:
            self.fields['ignore_server'].initial = ignore_server 
        else:
            self.fields['ignore_server'].initial = True
            
    FEATURE_NAME, ENVIRONMENT, SERVER_TYPE,IGNORE_SERVER, SERVER, FILE, CONFIG, FIELD_VALUE, FIELD_VALUE_LT, VALUE_TYPE, TIMER = ('feature_name','environment','server_type','ignore_server','server',
        'file','config','field_value','field_value_list','value_type','timer')
    INCLUDE_ALL_SERVERS = 'include_all_servers'  
         
    feature_name = forms.CharField(label='Feature Name', help_text='Please input feature name',required=False)        
    environment = forms.CharField(widget=forms.Select(), help_text='Please select the environment')
    server_type = forms.CharField(label='Server Type', widget=forms.Select(), help_text='Please select the server type')
    ignore_server = forms.BooleanField(label='Ignore Server', required=False)
    server = forms.CharField(widget=forms.Select(), help_text='Please select the server name')
    include_all_servers = forms.BooleanField(label='Include all servers', required=False)
    file = forms.CharField(widget=forms.Select(), help_text='Please select the file location')
    config = forms.CharField(widget=forms.Select(), help_text='Please select the configuration item')
    value_type = forms.CharField(widget=forms.Select(), help_text='Please select the value data type', required=False)
    field_value = forms.CharField(label='Field value', max_length=models.FIELD_VALUE_MAX, help_text='Please input value', required=False, strip=False)
    field_value_list = forms.CharField(label='Field value', widget=forms.Select(), help_text='Please select value', required=False) 
    timer = forms.IntegerField(label='Timer (Max 240 minutes [4 hours])', required=False, max_value = 240, min_value = 1)
    
class MakeRequestByFeatureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        environment_choices = kwargs.pop('environment_choices', None)
        team_choices = kwargs.pop('team_choices', None)
        super(MakeRequestByFeatureForm, self).__init__(*args, **kwargs)
        if environment_choices:
            reBuildChoiceWidget(environment_choices, self.fields['environment_f'] )
        if team_choices:
            reBuildChoiceWidget(team_choices, self.fields['team_f'] )
    ENVIRONMENT, FEATURE, FIELD_VALUE, FIELD_VALUE_LT, TIMER = ('environment_f','feature_f','field_value_f','field_value_list_f','timer_f')
    
    environment_f = forms.CharField(widget=forms.Select(), label='Environment', help_text='Please select the environment', max_length=100)
    team_f = forms.CharField(widget=forms.Select(), label='Team',help_text='Please select the team', max_length=100)
    feature_f = forms.CharField(widget=forms.Select(), label='Feature', help_text='Please select the feature', max_length=100)
    field_value_f = forms.CharField(label='Field value', max_length=models.FIELD_VALUE_MAX, help_text='Please select or input value', required=False)
    field_value_list_f = forms.CharField(label='Field value list', widget=forms.Select(), help_text='Please select value', required=False)
    timer_f = forms.IntegerField(label='Timer (Max 240 minutes [4 hours])', required=False, max_value = 240, min_value = 1)
    
class CMForm(forms.Form):
    def __init__(self, *args, **kwargs):
        environment_choices = kwargs.pop('environment_choices', None)
        action_choices = kwargs.pop('action_choices', None)
        super(CMForm, self).__init__(*args, **kwargs)
        if environment_choices:
            reBuildChoiceWidget(environment_choices, self.fields['environment'],True)
        if action_choices:
            reBuildChoiceWidget(action_choices, self.fields['action'])
    ACTION, ENVIRONMENT = ('action', 'environment')
    action = forms.CharField(widget=forms.Select(), label='Action', help_text='Please select the action', max_length=100)
    environment = forms.CharField(widget=forms.SelectMultiple(), label='Environment', help_text='Please select the environment', max_length=100)
