from .config import Project, Config, NoneConfig, CantAutomateConfig, CucumberConfig, SoapUIConfig, SpecflowConfig, SeeTestConfig

# For a more detailed guide on how to write Config classes, see '_TEMPLATE.py'

# GDMoney Project class.
# Do not modify.
class GDMoneyProject(Project):
    project_id = 67


# Common Config class that stores case fields shared by all automation types.
# Modify the 'common' property for fields which should display across all types.
class GDMoneyCommon(GDMoneyProject, Config):
    pass


# Automation Type Configs
# Add classes below by deriving from (1) GDMoneyCommon class, and (2) the corresponding automation type class.
# -----------------------



