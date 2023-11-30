from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig

# For a more detailed guide on how to write Config classes, see '_TEMPLATE.py'

# ATF Project class.
# Do not modify.
class ATFProject(Project):
    project_id = 3


# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class ATFCommon(ATFProject, Config):
    common = set()


# Automation Type Configs
# Add classes below by deriving from (1) ATFCommon class, and (2) the corresponding automation type class.
# -----------------------



