from django.http import Http404
from common_utils.testrail import APIError as TestRailAPIError
from common_utils import testrail_api
import sys
import traceback
from collections import OrderedDict, Iterable
from common_utils import configs
import inspect
import warnings
# AUTOMATION TYPE MAPPINGS AS LISTED IN TESTRAIL
_NO_AUTOMATION_TYPE = 'Manual'
_AUTOMATION_TYPE_MAPPING = {None: _NO_AUTOMATION_TYPE, 
                            1: "Can't Automate",
                            2: 'Cucumber',
                            3: 'SoapUI',
                            5: 'SeeTest',
                            6: "CucumberJVM",
                            7: "QuerySurge",
                            8: "Ranorex"
                        }



# CASE FIELD MACROS
CUST_AUTO_TYPE = 'custom_automation_type'
# ------------------------
class apiquery:
    """ Function decorator.
        Safeguard for calling TestRail API -utilizing functions.
    """
    _exception = Http404
    _print_traceback = False
    
    def __init__(self, function: callable):
        """ self._f is a function utilizing the TestRail API;
            e.g., any function from module testrail_api.
        """
        self._f = function
        
    def __call__(self, *args, **kwargs):
        """ Returns the result of calling self._f(*args, **kwargs).
            If an API exception is raised,
            catches and re-raises it an Http404 (by default) exception with an appropriate message.
        """        
        try:
            return self._f(*args, **kwargs)
        
        except TestRailAPIError:
            exc_type, exc_value = sys.exc_info()[:2]
            message = 'Failed to obtain results from TestRail API - caught exception while calling function "{0}(*{1}, **{2})":\n  {3}: {4}'.format(self._f.__name__, args, kwargs, exc_type, exc_value)
            if apiquery._print_traceback:
                traceback.print_exc()
            raise apiquery._exception(message)
        
    @classmethod
    def debug(cls, exc_to_raise: Exception) -> None:
        """ Set the exception to be raised upon TestRail error.
            Also enables original traceback printing upon exception.
            This should be used for testing only.
        """
        cls._exception = exc_to_raise
        cls._print_traceback = True
        
    @classmethod
    def reset(cls) -> None:
        """ Defaults exception back to Http404 and disables traceback debugging """
        cls._exception = Http404
        cls._print_traceback = False
        


@apiquery
def get_projects(**kwargs) -> {int: str}:
    """ Queries TestRail API for projects;
        returns an OrderedDict of {project_id: project_name},
        sorted by project name.
    """
    if kwargs.get('status') == 'completed':
        extra = "&is_completed=1"
    elif kwargs.get('status') == "all":
        extra = ""
    else:
        extra = "&is_completed=0"
        
    projects = testrail_api.get_project_map(extra)
    return OrderedDict(sorted(projects.items(), key=lambda pair: pair[1]))


@apiquery
def get_projects_by_email(email: str) -> {int: str}:
    """ Returns an OrderedDict of {project_id: project_name}, sorted by project name.
        Projects returned are projects that user with email address 'email' has access to.
    """
    projects = testrail_api.get_user_project_permissions(email)
    return OrderedDict(sorted(projects.items(), key=lambda pair: pair[1]))


def is_deprecated(name: str) -> bool:
    """ Returns True if name (suite or case) is deprecated;
        e.g. has 'ARCHIVED', 'DEPRECATED' in its name, or starts with 'Z_'.
    """
    name = name.upper()
    return any((name.startswith('Z_'), 'ARCHIVED' in name, 'DEPRECATED' in name))


@apiquery
def get_suites(project_id: int) -> {int: str}:
    """ Returns a dict {suite_id: suite_name}, based on project_id,
        sorted by suite name.
        Does not include deprecated/archived suites.
    """
    suites = testrail_api.get_suites_by_project(str(project_id))    
    suites = {suite['id']: suite['name'] for suite in suites if not is_deprecated(suite['name'])}
    if suites:
        suites = OrderedDict(sorted(suites.items(), key=lambda x:x[1]))
    return suites

@apiquery
def get_suites_raw(project_id: int) -> []:
    """ Returns a dict {suite_id: suite_name}, based on project_id,
        sorted by suite name.
        Does not include deprecated/archived suites.
    """
    suites = testrail_api.get_suites_by_project(str(project_id))    
    suites = [suite for suite in suites if not is_deprecated(suite['name'])]
    if suites:
        suites = sorted(suites, key = lambda x: x['name'])
    return suites

@apiquery
def get_cases(project_id: int, suite_id: int) -> [dict]:
    """ Returns a list of dicts (cases) from project, suite with project_id, suite_id """
    return testrail_api.get_cases_by_suite(str(project_id), str(suite_id))


def translate_automation_type(value: int or str) -> int or str:
    """ Returns the translated automation type (from field custom_automation_type)
        as its counterpart, using global _AUTOMATION_TYPE_MAPPING as its translation table.
        e.g., if value=2, returns 'Cucumber'.
              if value='Cucumber', returns 2.
        Returns _NO_AUTOMATION_TYPE if value is not mapped in the translation table.
    """
    mapping = _AUTOMATION_TYPE_MAPPING
    if type(value) is str:
        mapping = {v: k for k, v in mapping.items()}
        
    return mapping[value] if value in mapping else _NO_AUTOMATION_TYPE


def get_automation_types(cases: [dict]) -> {int: str}:
    """ Helper function to process Suite selection.
        Given list of dicts 'cases', 
        returns a dict of automation types mapped to their English name {testrail_automation_id: string_name}.
    """
    result = {}
    for case in cases:
        automation_type = case[CUST_AUTO_TYPE]
        result[automation_type] = translate_automation_type(automation_type)
    
    return result


def load_automation_types(response_list: [str]) -> (int,):
    """ Given response_list (JSON response of string number values or null), return a tuple representation
        with its contents eval'd to ints.
    """
    result = {int(i) for i in response_list if i.isdigit()}
    if 'null' in response_list:
        result.add(None)
    
    return tuple(result)


def parse_suites_for_automation_types(suite_ids: [int], project_id: int) -> {int: str}:
    """ Given suite_ids (keys of result of get_suites(...)), return a dict of
        {automation_type_id: automation_type_name} of all the types within these suites.
    """
    result = {}
    for suite_id in suite_ids:
        cases = get_cases(project_id, suite_id)
        result.update(get_automation_types(cases))
    
    return result


def generate_cases(suite_ids: [int], project_id: int, test_types: (int,)) -> [OrderedDict]:
    """ Returns a formatted list of all cases in suites within suite_ids,
        categorized (in order) with keys 'id', 'automation_type', 'Passed', 'Failed'.
        'Failed' fields are fields whose Python value is either None, or a 'falsy' iterable.
        ---
        test_types is a set of int automation type IDs to filter by.
    """        
    result = []
    for suite_id in suite_ids:
        cases = (case for case in get_cases(project_id, suite_id) if case[CUST_AUTO_TYPE] in test_types)
        for case in cases:
            automation_type = case[CUST_AUTO_TYPE]
            config = get_project_config(project_id, automation_type)
            
            filtered = OrderedDict([('id', case['id']), 
                                    (CUST_AUTO_TYPE, translate_automation_type(automation_type)),
                                    ('Passed', []), 
                                    ('Failed', [])
                                   ])
            
            # display all fields if either of the following:
            #   1) no Config class is found
            #   2) a Config class is defined but no fields (common or individual) are specified
            if config is None or not config.all():
                fields = case
            else:
                fields = (field for field in case if config.contains(field))
                
            def is_empty(field: str) -> bool:
                value = case[field]
                return value is None or (isinstance(value, Iterable) and not value)

            for field in fields:
                selector = 'Failed' if is_empty(field) else 'Passed'
                filtered[selector].append(configs.config.field_to_name(field))
            for selector in ('Passed', 'Failed'):
                filtered[selector].sort(key=lambda field: field.lower())
                
            result.append(filtered)
            
    return result


def get_config_classes() -> [configs.config.Config]:
    """ Returns a list of Project-Config classes from apps.testrail_report.configs """
    def filter_configs(member) -> bool:
        return inspect.isclass(member) and issubclass(member, configs.config.Config) and issubclass(member, configs.config.Project)

    result = []
    for name, module in inspect.getmembers(configs, lambda member: inspect.ismodule(member)):
        result += [cls for name, cls in inspect.getmembers(module, filter_configs)]
        
    for cls in result:
        cls.set_up_class()
        
    return result


def get_project_config(project_id: int, automation_type: int) -> configs.config.Config:
    """ Returns a Project-Config class with the corresponding project ID and automation type ID,
        or None if there is no match.
    """
    result = [cls for cls in get_config_classes() if cls.project_id == project_id and cls.automation_type == automation_type]
    if len(result) > 1:
        msg = 'multiple classes found with project_id={0} and automation_type={1}:\n  {2}'.format(project_id, automation_type, result)
        warnings.warn(msg)
        
    return result.pop() if result else None


def project_name(project_id: int, default='') -> str:
    """ Returns the project name of the project with project_id, with spaces converted to underscores.
        Or, if project_id is invalid, returns default.
    """
    projects = get_projects()
    return projects[project_id] if project_id in projects else default