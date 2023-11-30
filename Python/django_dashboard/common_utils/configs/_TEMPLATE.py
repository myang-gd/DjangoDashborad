# README
# ------
# This is a template for customizing the fields that will be displayed for a Project.
# For a working example (that's less overwhelmed with comments), see 'greendot.py'
#
# If there is no existing .py config file for the project you are seeking,
# copy & paste this file, rename it with the project's name, and modify it as necessary.
# ------

# Do not modify the following import statement.
from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig


# Change project_id to the appropriate project id.
# This can be found by navigating to the TestRail Dashboard.
# >> https://gdcqatestrail01/testrail/index.php?/dashboard
# 
# Click on the project, and examine the ID number in the url.
# For example, after clicking into the GreenDot project, the url is:
# >> https://gdcqatestrail01/testrail/index.php?/projects/overview/9
#
# which indicates that the project ID is 9.
class SampleProject(Project):
    project_id = -1


# Common Config class that stores case fields shared by all automation types.
# All fields designated will be displayed for every case.
# Fields specified must be their TestRail ID fields;
# for a full list, see TABLE in 'config.py'.
#
# Modify the 'common' property as necessary.
#
# In this case, all Cucumber, SoapUI, Specflow, etc. test cases under SampleProject
# will display these three fields.
class SampleCommon(SampleProject, Config):
    common = {'title',
              'suite_id',
              'priority_id'}


# Automation Type Configs
# The below classes are examples of how to implement automation-config classes.
# Each class will first derive from SampleCommon, then from its corresponding automation-type class:
#   CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig
#
# Specify the 'fields' to be displayed.
# It is important that the variable is named exactly 'fields'
# (likewise, in the Common class, the variable must be named exactly 'common').
# -----------------------

# SampleCantAutomateConfig specifies no fields,
# which means only its common fields will be displayed.
class SampleCantAutomateConfig(SampleCommon, CantAutomateConfig):
    pass


# SampleCucumberConfig specifies 2 fields,
# which means these two fields AND all common fields will be displayed.
class SampleCucumberConfig(SampleCommon, CucumberConfig):
    fields = {'custom_cucumber', 
              'custom_expected'}
    
