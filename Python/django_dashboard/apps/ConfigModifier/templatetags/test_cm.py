from django.test import TestCase
from django.contrib.messages import get_messages
from django.urls import reverse
import django
django.setup()
from apps.ConfigModifier import views

# Create your tests here.
class ConfigModifierTest(TestCase):
    def setUp(self):
        self.client.login(username='mzhao', password='')
    # parent path Subsidiary[2]  path SubsidiaryName  attribute InnerText   parent pass   should show parent dul waring no block
    def test_add_entry_xml_normal_node_indexparent_innertext(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'need_validate': ['on'], 'form-1-field_params': [''], 'form-0-field_value-2': [''], 'form-0-element_path': ['SubsidiaryName'], 'form-INITIAL_FORMS': ['0'], 'form-0-parent_id': [''], 'form-0-attribute': ['InnerText'], 'form-1-field_value-1': [''], 'node_type_add': ['4'], 'form-0-field_params': [''], 'form-0-field_value-1': [''], 'form-MAX_NUM_FORMS': ['1000'], 'form-TOTAL_FORMS': ['2'], 'form-1-attribute': [''], 'form-0-namespace': [''], 'form-1-element_path': ['Subsidiary[2]'], 'form-MIN_NUM_FORMS': ['1'], 'share_path': ['\\\\gdcqatools01\\GDCWeb\\IndexCheck.config'], 'submit_type': ['preview'], 'form-1-field_value-2': [''], 'csrfmiddlewaretoken': ['aVZRDzgzaRCFnRbvnNU9PfUyUQH66RhmFNRsbzUUlSkSXBXq6BGXD26ANkoP6g6w'], 'form-1-parent_id': [''], 'form-1-namespace': ['']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn('The entry you are adding [path: Subsidiary[2] ] already exists, duplicated entry will not be inserted', messages)
        self.assertEqual(resp.status_code, 200)
    # path: . attr: HandbackFilePath  failed because the node is under some child node
    def test_add_entry_json_normal_node_under_root(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\PSBFWebAPI\\appsettings.prf.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['HandbackFilePath'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['.']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertEqual(len(messages),0)
        self.assertEqual(resp.status_code, 200)
    def test_add_entry_json_array_node_under_root(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\ClientVersions.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['BuildNumber'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': ['"ApplicationID": 10043,"RequireUpgrade": "mandatory"'], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['.']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertEqual(len(messages),0)
        self.assertEqual(resp.status_code, 200)
    # path: . attr: ShowtoChampion  failed because the node is under some child node
    def test_add_entry_json_invalid_node_under_root(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\appsettings.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['ShowtoChampion'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['.']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn('Node does not exist path: $.ShowtoChampion, error: ', messages)
        self.assertEqual(resp.status_code, 200)
    # path: WF attr: OffsetRunTime search: "Name": "WF-Settlement"   parent SettlementConfigurations
    def test_add_entry_json_normal_node_with_parent_search(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'need_validate': ['on'], 'form-1-field_params': [''], 'form-0-field_value-2': [''], 'form-0-element_path': ['WF'], 'form-INITIAL_FORMS': ['0'], 'form-0-parent_id': [''], 'form-0-attribute': ['OffsetRunTime'], 'form-1-field_value-1': [''], 'node_type_add': ['4'], 'form-0-field_params': ['"Name": "WF-Settlement"'], 'form-0-field_value-1': [''], 'form-MAX_NUM_FORMS': ['1000'], 'form-TOTAL_FORMS': ['2'], 'form-1-attribute': [''], 'form-0-namespace': [''], 'form-1-element_path': ['SettlementConfigurations'], 'form-MIN_NUM_FORMS': ['1'], 'share_path': ['\\\\gdcqatools01\\GDCWeb\\appSettings.qag.json'], 'submit_type': ['preview'], 'form-1-field_value-2': [''], 'csrfmiddlewaretoken': ['rX2JiEBIReTqsGbZMe5hO4jSRHIjsI6vWPUkQEf32fBD2qXUv2R5CRvUKbp2s7VF'], 'form-1-parent_id': [''], 'form-1-namespace': ['']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertEqual(len(messages),0)
        self.assertEqual(resp.status_code, 200) 
    # json path properties[0] attr t
    def test_add_entry_json_normal_node_index(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\autofac.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['t'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['properties[0]']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertEqual(len(messages),0)
        self.assertEqual(resp.status_code, 200)
    # json path properties[0] attr t
    def test_add_entry_json_normal_node_index_child_array(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\appsettings.PIE.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['PartnerId'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['Partner[6]']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertEqual(len(messages),0)
        self.assertEqual(resp.status_code, 200)  
    # json path properties attr MaxFundingInParallel
    def test_add_entry_json_normal_node(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\autofac.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['MaxFundingInParallel'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['properties']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertEqual(len(messages),0)
        self.assertEqual(resp.status_code, 200)  
    # json path FraudManagementGateway attr BaseUrl
    def test_add_entry_dupe_json_node(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\CommentTest\\appsettings.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['ReCaptchaSiteKey'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['AppSettings']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn('The entry you are adding [path: AppSettings ] already exists, duplicated entry will not be inserted', messages)
        self.assertEqual(resp.status_code, 200)  
    # json path IsEligibilityCheckRequired[0] attr value
    def test_add_entry_invalid_attr_path_index(self):        
        resp = self.client.post(reverse(views.CONFIGMODIFIER_ENTRYADD, kwargs={}),{'share_path': ['\\\\gdcqatools01\\GDCWeb\\ExternalAccountManagement\\appsettings.json'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['1'], 'need_validate': ['on'], 'form-TOTAL_FORMS': ['1'], 'form-MAX_NUM_FORMS': ['1000'], 'form-0-attribute': ['value'], 'form-0-field_value-2': [''], 'csrfmiddlewaretoken': ['pCT9NVAPHhfwbFtunmID6PVptVzGa2cAUuLKlVeaSiXJLpfp6aurUC7rmpgpar1K'], 'form-0-remove_attribute': [''], 'form-0-field_params': [''], 'node_type_add': ['1'], 'form-0-remove_field': [''], 'form-0-parent_id': [''], 'form-0-namespace': [''], 'submit_type': ['preview'], 'form-0-field_value-1': [''], 'form-0-element_path': ['IsEligibilityCheckRequired[0]']}) 
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn('Node does not exist path: $..IsEligibilityCheckRequired[0].value, error: argument of type \'bool\' is not iterable', messages)
        self.assertEqual(resp.status_code, 200)  