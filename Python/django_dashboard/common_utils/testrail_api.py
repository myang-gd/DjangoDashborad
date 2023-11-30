from .testrail import APIClient



# Initialize Testrail info
testrail = APIClient('https://gdcqatestrail01/testrail/')
testrail.user = 'qa_test_automation@greendotcorp.com'
testrail.password = 'qa_test_automation'



def get_user_project_permissions(email, exclude = None):

    """
    Returns a dictionary of projects user has access to.
    
    email - User email
    exclude - Roles that will be excluded from the result.  If the user has a role in this list, any project tied to that role will not be returned. 
    """
    
    result = testrail.send_get('get_user_by_email&email=' + email)
    userID = result['id']
    
    try:
        testrail.v1 = True
        
        if exclude == None:
             result = testrail.send_get('get_user_project_permissions/get/' + str(userID))
        else:
             result = testrail.send_get('get_user_project_permissions/get/' + str(userID) + '&exclude=' + exclude.replace(' ', ''))
        
        if result['result'] == True:
            
            projects_dict = {}
            
            for project in result['userPermissions']:
                 projects_dict[project['project_id']] = project['project_name']
                 
            return projects_dict
    finally:
        testrail.v1 = False


def get_project_map(extra):
    
    """
    Returns a dictionary of all projects in Testrail where key is project id and value is project name.
    """
    
    result = testrail.send_get('get_projects' + extra)
    
    project_id_map = {}
    
    for project in result:
        project_id_map[project['id']] = project['name']
        
    return project_id_map


def get_milestones_by_project(project_id):
    
    return testrail.send_get('get_milestones/' + project_id + '&is_completed=0')    

    
def get_milestone_by_name(project_id, name):
    
    milestones = get_milestones_by_project(project_id)
    
    for milestone in milestones:
        if (milestone["name"] == name):
            return milestone
    
    return None


def get_suites_by_project(project_id):
    
    return testrail.send_get('get_suites/' + project_id)


def get_plans_by_milestone(project_id, milestone_id):
    
    return testrail.send_get('get_plans/' + project_id + '&milestone_id=' + str(milestone_id) + '&is_completed=0')


def get_plan(id):
    
    return testrail.send_get('get_plan/' + id)


def get_plan_by_name(project_id, milestone_id, name, add=True):
    
    plans = get_plans_by_milestone(project_id, milestone_id)
    
    plan_found = None
    
    for plan in plans:
        if (plan["name"] == name):
            plan_found = plan
        
    if (plan_found):
        return plan_found
    elif (add == True):
        return add_plan(project_id, milestone_id, name)
    return None    


def add_plan(project_id, milestone_id, name):
    
    data = { 'name': name, 'milestone_id': milestone_id }
    
    return testrail.send_post('add_plan/' + project_id, data)
    
    
def add_plan_entry(plan_id, entry):
    
    return testrail.send_post('add_plan_entry/' + str(plan_id), entry)


def get_tests_by_run(runId):
    
    return testrail.send_get('get_tests/' + str(runId))


def get_sections_by_suite(project_id, suite_id):
    
    return testrail.send_get('get_sections/' + project_id + '&suite_id=' + suite_id);


def get_cases_by_suite(project_id, suite_id):

    return testrail.send_get('get_cases/' + str(project_id) + '&suite_id=' + str(suite_id));


def get_cases_by_section(project_id, suite_id, section_id):

    return testrail.send_get('get_cases/' + project_id + '&suite_id=' + suite_id + '&section_id=' + section_id);

def get_case(case_id):
    
    return testrail.send_get('get_case/' + str(case_id));

    
def get_configs_by_project(project_id):

    return testrail.send_get('get_configs/' + project_id)
    
    
def get_run(run_id):
    
    return testrail.send_get('get_run/' + str(run_id))


def get_run_config(run_id):
    
    try:
        
        testrail.v1 = True
        
        result = testrail.send_get('run_configuration/get/' + str(run_id))

        if result['result'] == True:     
            return result['configuration']
        
    finally:
        
        testrail.v1 = False
    
    
def get_test(test_id):
    
    return testrail.send_get('get_test/' + str(test_id))
    
    



    
    