# -------
# Users do not modify the contents of this file.
# -------
# 
# Open to a more efficient (in space) approach;
# the current implementation's lookup methods
# execute in Θ(1) time but require O(mn) space,
# ('m' being the number of derived Config classes created,
#  which is the number of projects stored).


# Master dictionary of all TestRail case fields.
# {testrail_name: english_name}
TABLE = \
{
  'created_by': 'Created By', 
  'created_on': 'Created On', 
  'custom_automated_test_id': 'Automated Test ID', 
  'custom_automation_type': 'Automation Type', 
  'custom_casedesc': 'Test Case Description', 
  'custom_cant_automate': "Can't Automate", 
  'custom_class_name': 'Junit Custom Class Name', 
  'custom_cucumber': 'Cucumber', 
  'custom_cucumber_ips': 'Cucumber IPS',
  'custom_cucumber_version': 'Cucumber Version', 
  'custom_cust_test_case_cat': 'Test Case Category', 
  'custom_cust_test_case_type': 'Test Case Type', 
  'custom_custom_teststepname': 'teststepname', 
  'custom_domain': 'Domain', 
  'custom_expected': 'Expected Result', 
  'custom_ips_enabled': 'IPS Enabled', 
  'custom_keyword_test_steps': 'Keyword Test Steps', 
  'custom_method_signature': 'Junit Custom Method Signature', 
  'custom_needs_tsys_pingrabber': 'Needs Tsys Pingrabber', 
  'custom_parent_reference': 'Parent Reference', 
  'custom_pingrabber_load_amount': 'Pingrabber Load Amount', 
  'custom_pingrabber_payment_type': 'Pingrabber Payment Type', 
  'custom_pingrabber_product_code': 'Pingrabber Product Code QA', 
  'custom_pingrabber_product_code_qafour': 'Pingrabber Product Code QA4', 
  'custom_pingrabber_reload': 'Pingrabber Reload?', 
  'custom_platform': 'Platform',
  'custom_preconds': 'Preconditions', 
  'custom_qa_reviewed': 'QA Reviewed', 
  'custom_ref_over': 'Reference Overflow', 
  'custom_rich_sql_query': 'SQL Query (Rich)', 
  'custom_scenario': 'Scenario', 
  'custom_soapui_sqlquery': 'SQL Query (SoapUI)', 
  'custom_soapui_testcase_name': 'SoapUI TestCase Name', 
  'custom_soapui_teststeps': 'SoapUI Test Steps', 
  'custom_sprint': 'Sprint', 
  'custom_steps': 'Steps', 
  'custom_suitedesc': 'Suite Description', 
  'custom_tc_version': 'TC Version',
  'custom_test_design_complete': 'Test design complete', 
  'custom_test_environments': 'Test Environments White List', 
  'custom_test_sql_query': 'SQL Query', 
  'custom_use_case': 'Use Case', 
  'estimate': 'Estimate', 
  'estimate_forecast': 'Estimate Forecast', 
  'id': 'ID', 
  'milestone_id': 'Milestone', 
  'priority_id': 'Priority', 
  'refs': 'References', 
  'section_id': 'Section', 
  'suite_id': 'Suite ID', 
  'title': 'Title', 
  'type_id': 'Type', 
  'updated_by': 'Updated By', 
  'updated_on': 'Updated On'
}


# -------------------
# <Helper Functions>
def field_to_name(field: str) -> str:
    """ Given field, a name as listed in the TestRail API's JSON response,
        return the English name as per TABLE.
        Returns itself if there is no English name provided.
    """
    return TABLE[field] if field in TABLE else field

# -------------------


class Project:
    project_id = int()


class Config:
    automation_type = int()
    common = set()
    fields = set()
    
    @classmethod
    def all(cls) -> {str}:
        """ Returns a set of all common and specific fields """
        return cls.common.union(cls.fields)
    
    @classmethod
    def contains(cls, field: str) -> bool:
        """ Returns True if field is in the class' defined fields (including common) """
        return field in cls.all()
    
    @classmethod
    def set_up_class(cls) -> None:
        """ Ensures fields and common are sets """
        if not isinstance(cls.common, set):
            cls.common = set(cls.common)
        if not isinstance(cls.fields, set):
            cls.fields = set(cls.fields)
    


class NoneConfig(Config):
    automation_type = None


class CantAutomateConfig(Config):
    automation_type = 1
    
    
class CucumberConfig(Config):
    automation_type = 2
    
    
class SoapUIConfig(Config):
    automation_type = 3
#     common = {'custom_cust_test_case_cat',
#               'custom_cust_test_case_type',
#               'custom_preconds',
#               'custom_steps',
#               'custom_expected',
#               'custom_suitedesc',
#               'custom_casedesc',
#               'milestone_id',
#               'priority_id',
#               'refs',
#               'custom_soapui_testcase_name',
#               'custom_soapui_teststeps'}
    

class SpecflowConfig(Config):
    automation_type = 4
    
    
class SeeTestConfig(Config):
    automation_type = 5
#     common = {'custom_cust_test_case_cat', 
#               'custom_cust_test_case_type', 
#               'custom_preconds', 
#               'custom_steps', 
#               'custom_expected', 
#               'custom_platform', 
#               'milestone_id', 
#               'priority_id', 
#               'custom_class_name', 
#               'custom_method_signature'}
    
    