from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig

# For a more detailed guide on how to write Config classes, see '_TEMPLATE.py'

# GoBank Project class.
# Do not modify.
class GoBankProject(Project):
    project_id = 33


# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class GoBankCommon(GoBankProject, Config):
    common = set()


# Automation Type Configs
# Add classes below by deriving from (1) GoBankCommon class, and (2) the corresponding automation type class.
# -----------------------



