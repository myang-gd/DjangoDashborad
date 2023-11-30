from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig

# For a more detailed guide on how to write Config classes, see '_TEMPLATE.py'

# Card Management Project class.
# Do not modify.
class CardManagementProject(Project):
    project_id = 63


# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class CardManagementCommon(CardManagementProject, Config):
    common = set()


# Automation Type Configs
# Add classes below by deriving from (1) CardManagementCommon class, and (2) the corresponding automation type class.
# -----------------------



