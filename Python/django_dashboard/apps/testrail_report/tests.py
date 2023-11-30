# # # setup Django testing environment
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_dashboard.settings')
import django
django.setup()
# # #

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponse
from apps.testrail_report import views, configs
import json
import pathlib
import random
import unittest
import warnings


class TestAPICalls(unittest.TestCase):
    """ TestAPICalls derives from unittest.TestCase instead of django.test.TestCase
        because the testrail_report app uses no local database;
        django.test.TestCase sets up a test-database every time the unit tests are run.
    """
    @classmethod
    def setUpClass(cls):
        views.apiquery.debug(AssertionError)
        cls._ajax_macro = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
          
    @classmethod
    def tearDownClass(cls):
        views.apiquery.reset()
        
    def setUp(self):
        # sample email address used to get projects
        self._email = 'gko@greendotcorp.com'
        
    def tearDown(self):
        views.ReportView.reset()
        
        msg = 'views.ReportView.reset() failed'
        self.assertIsNone(views.ReportView.project_id, msg)
        self.assertIsNone(views.ReportView.suite_ids, msg)
        
        
    def _skip_if_login_required(self, response_code: int):
        if response_code == 302:
            self.skipTest('disable authentication before running unit tests; comment out ReportView.dispatch(...) decorators')
                
                
    def _simulate_request(self, **data) -> HttpResponse:
        factory = RequestFactory()
        request = factory.get('', data=data, **self._ajax_macro)
        request.user = AnonymousUser()
        request.user.email = self._email
        
        self.assertEqual(1, len(request.GET), 'received extraneous responses: {0}'.format(request.GET))
        response = views.ReportView.as_view()(request)
        
        # 200 = successful response code
        self._skip_if_login_required(response.status_code)
        self.assertEqual(200, response.status_code, 'simulated request with data={0} failed with response code {1}'.format(data, response.status_code))
         
        return response
     
     
    def _deserialize_response(self, response, decoding='utf-8') -> dict:
        return json.loads(str(response.content, decoding))
     
    def test_is_site_alive(self):
        factory = RequestFactory()
        request = factory.get('')
        request.user = AnonymousUser()
        request.user.email = self._email
        response = views.ReportView.as_view()(request)
          
        # 200 = successful response code
        self._skip_if_login_required(response.status_code)
        self.assertEqual(200, response.status_code, 'simulated site check failed with response code {0}'.format(response.status_code))
          
          
    def test_simulate_gd_project_selection(self, project_id=9):
        """ GreenDot project ID is 9 """
        data = {'project_id': project_id}
        response = self._simulate_request(**data)
        post = self._deserialize_response(response)
        self.assertIn('suites', post)
        self.assertTrue(post['suites'])
           
           
    def test_simulate_gd_suites_selection(self, suites=['158']):
        self.test_simulate_gd_project_selection()
           
        data = {'suite_ids[]': suites}
        response = self._simulate_request(**data)
        post = self._deserialize_response(response)
        self.assertIn('automation_types', post)
           
           
    def test_simulate_gd_select_cucumber(self):
        self.test_simulate_gd_project_selection()
        self.test_simulate_gd_suites_selection()
           
        data = {'automation_types[]': ['2']}
        response = self._simulate_request(**data)
        post = self._deserialize_response(response)
        self.assertIn('cases', post)
           
           
    def test_export_path_exists(self):
        path = pathlib.Path(views._EXPORT_SAVE_DIR)
        self.assertTrue(path.is_dir(), 'path {0} does not exist; Excel export will fail'.format(views._EXPORT_SAVE_PATH))
           
           
    def test_simulate_gd_cucumber_export(self):
        path = pathlib.Path(views._EXPORT_SAVE_PATH)
        original_mod_time = path.stat().st_mtime if path.is_file() else -1
           
        self.test_simulate_gd_select_cucumber()
           
        path = pathlib.Path(views._EXPORT_SAVE_PATH)
        new_mod_time = path.stat().st_mtime
        self.assertTrue(path.is_file(), 'export failed')
        self.assertGreater(new_mod_time, original_mod_time, 'file modification times conflict; newly exported file time <= old file time')
          
          
    def test_simulate_download(self):
        factory = RequestFactory()
        request = factory.get('/download')
        request.user = AnonymousUser()
        response = views.download(request)
                  
        self.assertEqual(200, response.status_code, "url 'download' failed")
        self.assertIn('Content-Length', response)
        self.assertIn('Content-Disposition', response)
         
         
    def test_is_deprecated(self):
        a = 'test_case_Name'
        b = 'z_Example_Project'
        c = 'suite_is_archived'
        d = 'this_is_DEPRECateD'
          
        self.assertFalse(views.is_deprecated(a))
        self.assertTrue(views.is_deprecated(b))
        self.assertTrue(views.is_deprecated(c))
        self.assertTrue(views.is_deprecated(d))
                             
                            
    def test_translate_automation_type_all(self):
        mapping = views._AUTOMATION_TYPE_MAPPING.copy()
                                 
        for i in mapping:
            self.assertEqual(mapping[i], views.translate_automation_type(i))
                     
        mapping = {k: v for k, v in mapping.items() if type(k) is int}
        minimum = min(mapping)
        maximum = max(mapping) + 1
                     
        for _ in range(5):      # run this test 5 times
            r = minimum 
            while r in mapping:
                r = random.randrange(minimum - 100, maximum + 100)     # generate random invalid number
            self.assertEqual(views._NO_AUTOMATION_TYPE, views.translate_automation_type(r))
                    
                    
    def test_translate_automation_type(self):
        self.assertEqual(views._NO_AUTOMATION_TYPE, views.translate_automation_type(None))
        self.assertEqual("Can't Automate", views.translate_automation_type(1))
        self.assertEqual('Cucumber', views.translate_automation_type(2))
        self.assertEqual('SoapUI', views.translate_automation_type(3))
        self.assertEqual('Specflow', views.translate_automation_type(4))
        self.assertEqual('SeeTest', views.translate_automation_type(5))
                
                
    def test_translate_automation_type_str(self):
        self.assertEqual(None, views.translate_automation_type(views._NO_AUTOMATION_TYPE))
        self.assertEqual(1, views.translate_automation_type("Can't Automate"))
        self.assertEqual(2, views.translate_automation_type('Cucumber'))
        self.assertEqual(3, views.translate_automation_type('SoapUI'))
        self.assertEqual(4, views.translate_automation_type('Specflow'))
        self.assertEqual(5, views.translate_automation_type('SeeTest'))
                
            
    def test_translate_automation_type_invalid(self):
        r = random.randrange(-100, -1)
        self.assertEqual(views._NO_AUTOMATION_TYPE, views.translate_automation_type(r))
        self.assertEqual(views._NO_AUTOMATION_TYPE, views.translate_automation_type('test'))
                                         
                             
    def test_get_projects_is_sorted(self):
        projects = views.get_projects_by_email(self._email)
        as_list = sorted(projects.items(), key=lambda pair: pair[1])
        self.assertSequenceEqual(list(projects.items()), as_list, seq_type=list, msg='projects appear to be out of order; should be sorted alphabetically:\n  {0}'.format(projects))
                                  
                                  
    def test_get_suites_includes_no_deprecated_suites(self):
        GD_project_id = 9
        suites = views.get_suites(GD_project_id)
        self.assertTrue(suites)
                                  
        for name in suites.values():
            name = name.upper()
            self.assertNotIn('ARCHIVED', name)
            self.assertNotIn('DEPRECATED', name)
                                      
                                      
    def test_get_automation_types(self):
        GD_project_id = 9
        expected_automation_types = {1, 2, 3}
        found_automation_types = expected_automation_types.copy()
        interesting_cases = []
                             
        # analyze suites in GD project until one case of each expected automation type is found
        try:
            for suite_id in views.get_suites(GD_project_id):
                cases = (case for case in views.get_cases(GD_project_id, suite_id) if case[views.CUST_AUTO_TYPE] in expected_automation_types)
                for case in cases:
                    if not found_automation_types:
                        raise StopIteration
                    automation_type = case[views.CUST_AUTO_TYPE]
                    found_automation_types.discard(automation_type)
                    interesting_cases.append(case)
                               
        except StopIteration:
            pass
                             
        else:
            self.assertFalse(found_automation_types, 'automation type(s) not found in project (ids: {0});\n  try changing project?'.format(found_automation_types))
                             
        # compare found cases against result of views.get_automation_types(...)
        result = views.get_automation_types(interesting_cases)
        self.assertTrue(result)
                             
        result_ids_only = set(result)
        self.assertSetEqual(expected_automation_types, result_ids_only)
                             
        # ensure ids/names of results are correctly mapped
        result_names_only = set(result.values())
        self.assertIn(1, result)
        self.assertIn("Can't Automate", result_names_only)
        self.assertIn(2, result)
        self.assertIn('Cucumber', result_names_only)
        self.assertIn(3, result)
        self.assertIn('SoapUI', result_names_only)
                                  
                          
    def test_get_cases_with_criteria_as_cucumber_cases_only(self):
        GD_project_id = 9
        sample_suite_id = 158
                          
        def is_cucumber(case: dict) -> bool:
            value = case[views.CUST_AUTO_TYPE]
            flag = type(value) is int or value is None
            self.assertTrue(flag, 'expected API results to return int test type value (or None);\n received type {0} ({1})'.format(type(value), value))
            return value == 2     # Cucumber
                                  
        cases = (case for case in views.get_cases(GD_project_id, sample_suite_id) if is_cucumber(case))
        for case in cases:
            self.assertEqual(2, case[views.CUST_AUTO_TYPE])
                                    
                           
    def test_case_field_translation_table_exists(self):
        self.assertTrue(configs.config.TABLE, 'reading of translation table file failed; see apps.testrail_report.configs.config')
                                                   
                           
    def test_case_field_translation(self):
        self.assertEqual('ID', configs.config.field_to_name('id'))
        self.assertEqual('Title', configs.config.field_to_name('title'))
        self.assertEqual('Cucumber', configs.config.field_to_name('custom_cucumber'))
        self.assertEqual('References', configs.config.field_to_name('refs'))
        self.assertEqual('Test Case Description', configs.config.field_to_name('custom_casedesc'))
                             
        self.assertEqual('test', configs.config.field_to_name('test'))
        self.assertEqual('abc', configs.config.field_to_name('abc'))
                                 
                             
    def test_generate_cases_gd(self):
        GD_project_id = 9
        sample_suite_id = 158
        cases = views.generate_cases([sample_suite_id], GD_project_id, {1, 2, 3})
        table_set = {item for item in list(configs.config.TABLE) + list(configs.config.TABLE.values())}
                                 
        for case in cases:
            for field in case['Passed'] + case['Failed']:
                self.assertIn(field, table_set, msg='unexpected field {0} identified; not found in configs.config.TABLE'.format(field))
                              
                              
    def test_all_configs_fields_are_valid(self):
        for config in views.get_config_classes():
            for field in config.all():
                self.assertIn(field, configs.config.TABLE, 'Config class {0} has an invalid field: {1}'.format(config, field))
                                   
                                   
    def test_config_fields_is_set(self):
        for config in views.get_config_classes():
            msg = "efficiency warning: change Config class {0} 'fields' property to {1} for O(1) performance; currently is {2}".format(config, set, type(config.fields))
            self.assertIsInstance(config.fields, set, msg)
            self.assertIsInstance(config.common, set, msg)
                            
                            
    def test_get_project_config_gd_cucumber(self):
        gd_project_id = 9
        cucumber_id = 2
        config = views.get_project_config(gd_project_id, cucumber_id)
                     
        self.assertIsNotNone(config, "views.get_project_config(...) returned None; should have returned 'GreenDotCucumberConfig'")
        self.assertTrue(hasattr(config, 'project_id'))
        self.assertTrue(hasattr(config, 'automation_type'))
        self.assertTrue(hasattr(config, 'fields'))
        self.assertTrue(hasattr(config, 'common'))
        self.assertEqual(gd_project_id, config.project_id)
        self.assertEqual(cucumber_id, config.automation_type)
                           
                           
    def test_get_project_config_invalid_project_id(self):
        invalid_project_id = random.randrange(-100, 0)
        automation_type = random.randrange(1, len(views._AUTOMATION_TYPE_MAPPING))
        config = views.get_project_config(invalid_project_id, automation_type)
        self.assertIsNone(config, 'views.get_project_config(project_id={0}, automation_type={1}) returned {2}; should have returned None'.format(invalid_project_id, automation_type, config))
                 
                 
    def test_get_project_config_invalid_automation_type(self):
        gd_project_id = 9
        invalid_automation_type = random.randrange(-100, -1)
        config = views.get_project_config(gd_project_id, invalid_automation_type)
        self.assertIsNone(config, 'views.get_project_config(project_id={0}, automation_type={1}) returned {2}; should have returned None'.format(gd_project_id, invalid_automation_type, config))
                
              
    def test_one_result_per_project_id_and_automation_id(self):
        project_ids = views.get_projects_by_email(self._email).keys()
        for project_id in project_ids:
            for automation_id in views._AUTOMATION_TYPE_MAPPING:
                with warnings.catch_warnings(record=True) as w:
                    config = views.get_project_config(project_id, automation_id)
                    msg = 'warning raised from project with id={0}, automation_type={1}'.format(project_id, automation_id)
                    self.assertEqual(0, len(w), msg)
   
                    if config is not None:
                        self.assertTrue(issubclass(config, configs.config.Project))
                        self.assertTrue(issubclass(config, configs.config.Config))
         

  
  
if __name__ == '__main__':
    unittest.main()
