from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig
 
# Walmart Project class.
# Do not modify.
class WalmartProject(Project):
    project_id = 11
    
    
# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class WalmartCommon(WalmartProject, Config):
    common = set()
     
 
# Automation Type Configs
# Modify the following classes' 'fields' properties as necessary.
# -----------------------
class WalmartCantAutomateConfig(WalmartCommon, CantAutomateConfig):
    pass
 
 
class WalmartCucumberConfig(WalmartCommon, CucumberConfig):
    fields = {'section_id', 
              'priority_id', 
              'milestone_id', 
              'refs', 
              'custom_cust_test_case_type', 
              'custom_tc_version',            
              'custom_sprint', 
              'custom_platform', 
              'custom_steps', 
              'custom_expected'}
     
     
class WalmartSoapUIConfig(WalmartCommon, SoapUIConfig):
    pass

