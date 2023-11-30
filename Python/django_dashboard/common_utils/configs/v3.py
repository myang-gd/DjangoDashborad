from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig

# For a more detailed guide on how to write Config classes, see '_TEMPLATE.py'

# V3 Project class.
# Do not modify.
class V3Project(Project):
    project_id = 29


# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class V3Common(V3Project, Config):
    common = set()


# Automation Type Configs
# Add classes below by deriving from (1) V3Common class, and (2) the corresponding automation type class.
# -----------------------



