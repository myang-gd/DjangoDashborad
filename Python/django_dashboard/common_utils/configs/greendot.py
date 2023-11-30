from .config import Project, Config, CantAutomateConfig, CucumberConfig, SoapUIConfig, NoneConfig

# Green Dot Project class.
# Do not modify.
class GreenDotProject(Project):
    project_id = 9
    

# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class GreenDotCommon(GreenDotProject, Config):
    common = {'priority_id', 
              'refs', 
              'custom_cust_test_case_type',
              'custom_cust_test_case_cat', 
              'custom_steps', 
              'custom_expected',
              'custom_qa_reviewed'}


# Automation Type Configs
# Add classes below by deriving from (1) GreenDotCommon class, and (2) the corresponding automation type class.
# -----------------------
class GreenDotCantAutomateConfig(GreenDotCommon, CantAutomateConfig):
    pass


class GreenDotCucumberConfig(GreenDotCommon, CucumberConfig):
    fields = {'custom_cucumber'}
    
    
class GreenDotSoapUIConfig(GreenDotCommon, SoapUIConfig):
    fields = {'custom_soapui_teststeps', 
              'custom_soapui_sqlquery'}

class GreenDotNoneConfig(GreenDotCommon, NoneConfig):
    pass

