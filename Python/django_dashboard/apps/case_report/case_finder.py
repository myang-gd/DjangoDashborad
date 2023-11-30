import threading
import logging
from django.core.cache import cache
from collections import OrderedDict
from common_utils.xml_util import XmlUtil
from common_utils.peforce import Perforce
from common_utils import testrail_api,testrail_util
from apps.case_report.logger import Logger
import concurrent.futures

SETTING_FILE = 'settings.xml'
ELEMENT_ORDER_FILE = 'element.order'
XPATH_PROJECT_NAME = '/con:soapui-project/@name'
XPATH_SUITE_NAME = '/con:testSuite/@name'
XPATH_CASE_NAME = '/con:testCase/@name'
XPATH_CASE_ID = '/con:testCase/@id'
XPATH_SECURITY_NAME ='/con:securityTest/@name'
XPATH_SECURITY_CASE_ID ='/con:securityTest/@testCaseId'
XPATH_SETTING = '/' + SETTING_FILE

FIELD_DIR = 'dir'
FIELD_DEPOT_FILE = 'depotFile'
NAME_SPACE = {'con':'http://eviware.com/soapui/config'}

## TestRail constant
D_ID = 'id'
D_TITLE = 'title'
D_SECTION_ID = 'section_id'
D_SECTION = 'section'
D_SUITE = 'suite'
D_NAME = 'name'
D_AUTO_TYPE = 'custom_automation_type'
D_CASE_LIST = 'case_list'
D_SUITE_LIST = 'suite_list'
D_SECTIONS_MAP = 'sections_map'
D_DEFAULT_SECTION = 'default_section'
D_SECURITY_CASE_ID = 'testCaseId'

_NO_AUTOMATION_TYPE = 'Manual'
_AUTOMATION_TYPE_MAPPING = {None: _NO_AUTOMATION_TYPE, 
                            1: "Can't Automate",
                            2: 'Cucumber',
                            3: 'SoapUI',
                            4: 'Specflow',
                            5: 'SeeTest'}
logger = logging.getLogger("case_report")

def find_cases_for_project(project_dir, p4:Perforce, tr_suite_list:[str]):

    Logger.log("Finding cases under project dir" + project_dir)
   
    # prepare  project_dir
    suite_list = []
    if project_dir.endswith('/'):
        project_dir = project_dir[:-1]
   
    # validate    
    settingFile = p4.read_file(project_dir + XPATH_SETTING)
    if not settingFile:
        return  suite_list
    projectName = XmlUtil.get_str_element(settingFile, XPATH_PROJECT_NAME,  NAME_SPACE)
    if not projectName :
        return  suite_list
    if tr_suite_list  and projectName not in tr_suite_list:
        Logger.log("return due to not in filter " + projectName)
        return  suite_list

    # support security test case
    security_tests = p4.get_subdirs(project_dir, True)
    security_test_list = []
    for security_test in security_tests:
        security_file_path= security_test[FIELD_DEPOT_FILE]
        if ELEMENT_ORDER_FILE in security_file_path or SETTING_FILE in security_file_path:
            continue
        else:
            security_file_bytes = p4.read_file(security_file_path)
            security_name = XmlUtil.get_str_element(security_file_bytes, XPATH_SECURITY_NAME,  NAME_SPACE)
            security_case_id = XmlUtil.get_str_element(security_file_bytes, XPATH_SECURITY_CASE_ID,  NAME_SPACE)
            if security_name:
                security_test_list.append({D_NAME : security_name, D_SECURITY_CASE_ID : security_case_id})
    
    # prepare returning cases      
    suite_dirs = p4.get_subdirs(project_dir)
    for suite_dir in suite_dirs:
        case_list = []
        settingFile = p4.read_file(suite_dir[FIELD_DIR] + XPATH_SETTING)
        if not settingFile:
            continue 

        suiteName = XmlUtil.get_str_element(settingFile, XPATH_SUITE_NAME,  NAME_SPACE)
        if not suiteName :
            continue
        case_files = p4.get_subdirs(suite_dir[FIELD_DIR], True)
        for case_file in case_files:
            file_path = case_file[FIELD_DEPOT_FILE] 
            if ELEMENT_ORDER_FILE in file_path or SETTING_FILE in file_path:
                continue
            else:
                case_file_bytes = p4.read_file(file_path)
                if not case_file_bytes:
                    continue
                caseName =  XmlUtil.get_str_element(case_file_bytes, XPATH_CASE_NAME,  NAME_SPACE)
                if not caseName:
                    continue
                if security_test_list:
                    caseId =  XmlUtil.get_str_element(case_file_bytes, XPATH_CASE_ID,  NAME_SPACE)
                    matched_security_tests = [security_test for security_test in security_test_list if security_test[D_SECURITY_CASE_ID] == str(caseId)]
                    for security_test in  matched_security_tests:
                        case_list.append({D_NAME : ('%s (%s -> %s)' %(security_test[D_NAME], suiteName, caseName))})
                        security_test_list.remove(security_test)
              
                
                case_list.append({D_NAME : caseName })
        suite_list.append({D_NAME : suiteName, D_CASE_LIST : case_list}) 
    
    logger.info('Finished project ' + projectName)
    
    return {D_NAME : projectName, D_SUITE_LIST : suite_list}


def find_cases_for_projects(root_path_list:[str], p4:Perforce, progress_id, suite_list:[str]): 
    """
    suite_list is TestRail suite name list as filter to reduce time consuming 
    root_path_list is p4 path list for searching ReadyAPI test cases e.g. //QA/READYAPI/Projects/Platform/    
    """
    # find project all the project directories 
    project_dirs = [] 
    setProgress(progress_id, 2)
    Logger.log("Finding projects from p4 under : " + str(root_path_list))
    try:
        for path in root_path_list:
            project_dirs.extend(p4.find_project_dirs_none_recur(path))
    except Exception as e:
        Logger.log("Failed to find ReadyAPI projects from p4 due to " + str(e))
    
    setProgress(progress_id, 10)
    Logger.log("Total ReadyAPI projects found in P4: " + str(len(project_dirs)))
    
    # process each project directory to find test cases
    project_list = []
    total_count = len(project_dirs)
    pre_progress = getProgress(progress_id)
    process_count = 0
    try:
        for project_dir in project_dirs :
            cases = find_cases_for_project(project_dir, p4,suite_list)
            if cases:
                project_list.append(cases)
            process_count += 1
            progress = int((process_count/total_count*100.0)*0.4) + pre_progress
            setProgress(progress_id, progress)     
    except Exception as e:
        Logger.log('Failed to get cases from path %s due to %s' %(str(root_path_list), str(e)))
    finally:
        p4.release()
         
    return  project_list
def isCaseInP4(caseName, suiteName, P4_suite_list:list):  
    p4_suite =  next((suite for suite in P4_suite_list if suite[D_NAME] == str(suiteName)), None)
    if p4_suite and next((case for case in p4_suite[D_CASE_LIST] if case[D_NAME] == caseName), None):
        return True
    else:
        return False
def find_unused_cases(p_id:str, root_path_list:[str], p4:Perforce, progress_id, suite_ids:[str], is_all_cases:[bool]):
    setProgress(progress_id, 0)
    # check if cache works
    if getProgress(progress_id) != 0 :
        Logger.log('Memcache is not started, finding unused case is canceling')
        return []
    
    suite_list = testrail_util.get_suites_raw(int(p_id));  
    if suite_ids:
        suite_list = [suite for suite in suite_list if str(suite[D_ID]) in suite_ids]
    if (not suite_list) or len(suite_list) == 0:
        suite_list = []   
    suite_name_list = [suite[D_NAME] for suite in suite_list]
    
    progress_factor = 0.5
    if is_all_cases:
        project_list_p4 = []
        progress_factor = 1
    else:
        project_list_p4 = find_cases_for_projects(root_path_list, p4, progress_id, suite_name_list)
    
    project_list = []
    total_count = len(suite_list)
    pre_progress = getProgress(progress_id)
    total_cases = []
    for suite in suite_list:
        Logger.log('Finding unused cases for TestRail suite ' + str(suite[D_NAME]))
        suite_list_temp = []
        sections = testrail_api.get_sections_by_suite(p_id, str(suite[D_ID]))
        p4_project = next((project for project in project_list_p4 if project[D_NAME] == str(suite[D_NAME])), None)
        p4_suite_list = []
        if p4_project:
            p4_suite_list = p4_project[D_SUITE_LIST]
        sections_map = {}
        for section in sections:   
            sections_map[section[D_ID]] = section[D_NAME]
        cases = testrail_api.get_cases_by_suite(p_id, str(suite[D_ID]));
        case_names = []
        if is_all_cases:
            case_names = [OrderedDict([(D_ID, str(case[D_ID])), (D_TITLE, case[D_TITLE]), (D_SECTION, sections_map[case[D_SECTION_ID]]), (D_SUITE, suite[D_NAME]),(D_AUTO_TYPE, _AUTOMATION_TYPE_MAPPING.get(case[D_AUTO_TYPE]))]) for case in cases if not isCaseInP4(case[D_TITLE], sections_map[case[D_SECTION_ID]], p4_suite_list)]
        if cases and is_all_cases:
            for case in cases:
                case_names.append(OrderedDict([(D_ID, str(case[D_ID])), (D_TITLE, case[D_TITLE]), (D_SECTION, sections_map[case[D_SECTION_ID]]), (D_SUITE, suite[D_NAME]),(D_AUTO_TYPE, _AUTOMATION_TYPE_MAPPING.get(case[D_AUTO_TYPE]))]))
        elif cases:
            cases = [ case for case in cases if case['custom_automation_type'] == 3 ] # only include Automation Type = 'SoapUI'
            case_names = [OrderedDict([(D_ID, str(case[D_ID])), (D_TITLE, case[D_TITLE]), (D_SECTION, sections_map[case[D_SECTION_ID]]), (D_SUITE, suite[D_NAME]),(D_AUTO_TYPE, _AUTOMATION_TYPE_MAPPING.get(case[D_AUTO_TYPE]))]) for case in cases if not isCaseInP4(case[D_TITLE], sections_map[case[D_SECTION_ID]], p4_suite_list)] 
        total_cases.extend(case_names)
        suite_list_temp.append({D_NAME : D_DEFAULT_SECTION,  D_CASE_LIST : case_names})
        project_list.append({D_NAME : str(suite[D_NAME]) , D_SUITE_LIST : suite_list_temp, D_SECTIONS_MAP : sections_map}) 
        progress = int((len(project_list)/total_count*100.0)*progress_factor) + pre_progress
        setProgress(progress_id, progress)
    return total_cases
def find_unused_cases_multithread(p_id:str, root_path_list:[str], p4:Perforce, progress_id, suite_ids:[str], is_all_cases:[bool]):
    setProgress(progress_id, 0)
    # check if cache works
    if getProgress(progress_id) != 0 :
        Logger.log('Memcache is not started, finding unused case is canceling')
        return []   
     
    suite_list = testrail_util.get_suites_raw(int(p_id));     
    if suite_ids:
        suite_list = [suite for suite in suite_list if str(suite[D_ID]) in suite_ids]
    if (not suite_list) or len(suite_list) == 0:
        suite_list = []   
    suite_name_list = [suite[D_NAME] for suite in suite_list]
    progress_factor = 0.5
    if is_all_cases:
        project_list_p4 = []
        progress_factor = 1
    else:
        project_list_p4 = find_cases_for_projects(root_path_list, p4, progress_id, suite_name_list)

    project_list = []
    total_count = len(suite_list)
    pre_progress = getProgress(progress_id)
    total_cases = []
            
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(find_unused_cases_runnable, p_id, suite, project_list_p4, is_all_cases): suite for suite in  suite_list}
        for future in concurrent.futures.as_completed(future_to_url):
            suite_map = future_to_url[future]
            try:
                total_cases_temp, project_list_temp = future.result()
                project_list.extend(project_list_temp)
                total_cases.extend(total_cases_temp)
                progress = int((len(project_list)/total_count*100.0)*progress_factor) + pre_progress
                setProgress(progress_id, progress)
            except Exception as exc:
                print('%s generated an exception: %s' % (str(suite_map[D_NAME]), exc)) 
            else:
                print('Finished to process %s' % (str(suite_map[D_NAME])))        
    return total_cases
def find_unused_cases_runnable(p_id:str, suite, project_list_p4, is_all_cases:[bool]):
    total_cases = []
    project_list = []
    Logger.log('Finding unused cases for TestRail suite ' + str(suite[D_NAME]))
    suite_list_temp = []
    sections = testrail_api.get_sections_by_suite(p_id, str(suite[D_ID]))
    p4_project = next((project for project in project_list_p4 if project[D_NAME] == str(suite[D_NAME])), None)
    p4_suite_list = []
    if p4_project:
        p4_suite_list = p4_project[D_SUITE_LIST]
    sections_map = {}
    for section in sections:   
        sections_map[section[D_ID]] = section[D_NAME]
    cases = testrail_api.get_cases_by_suite(p_id, str(suite[D_ID]));
    case_names = []
    if cases and is_all_cases:
        for case in cases:
            case_names.append(OrderedDict([(D_ID, str(case[D_ID])), (D_TITLE, case[D_TITLE]), (D_SECTION, sections_map[case[D_SECTION_ID]]), (D_SUITE, suite[D_NAME]),(D_AUTO_TYPE, _AUTOMATION_TYPE_MAPPING.get(case[D_AUTO_TYPE]))]))
    elif cases:
        cases = [ case for case in cases if case['custom_automation_type'] == 3 ] # only include Automation Type = 'SoapUI'
        case_names = [OrderedDict([(D_ID, str(case[D_ID])), (D_TITLE, case[D_TITLE]), (D_SECTION, sections_map[case[D_SECTION_ID]]), (D_SUITE, suite[D_NAME]),(D_AUTO_TYPE, _AUTOMATION_TYPE_MAPPING.get(case[D_AUTO_TYPE]))]) for case in cases if not isCaseInP4(case[D_TITLE], sections_map[case[D_SECTION_ID]], p4_suite_list)] 
    total_cases.extend(case_names)
    suite_list_temp.append({D_NAME : D_DEFAULT_SECTION,  D_CASE_LIST : case_names})
    project_list.append({D_NAME : str(suite[D_NAME]) , D_SUITE_LIST : suite_list_temp, D_SECTIONS_MAP : sections_map}) 
    return total_cases, project_list
lock = threading.Lock() 
def setProgress(x_progress_id, _progress:int):
    lock.acquire()
    cache.set(x_progress_id, _progress) 
    lock.release()
def getProgress(x_progress_id):
    return  cache.get(x_progress_id)

def clearProgress(x_progress_id):
    lock.acquire()
    try:
        cache.delete(x_progress_id)
        cache.delete(x_progress_id + '_cancel')
    except:
        pass
    lock.release()
    