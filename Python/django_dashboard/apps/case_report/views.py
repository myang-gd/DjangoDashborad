import json
import mimetypes
import os.path
import warnings
import wsgiref.util
import time
from django.core.cache import cache
from django.shortcuts import render
from django.http.response import HttpResponse
from django.http import Http404
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.case_report import export
from collections import OrderedDict
from .case_finder_thread import FinderThread
from django.contrib import messages
from apps.case_report.logger import Logger
from common_utils import testrail_util
from common_utils.django_util import Django_Util
# TestRail project perforce location map
_TR_PROJECT_P4_MAPPING = {  25: { 'name':'Platform', 'p4_path_list':['//QA/READYAPI/Projects/Platform/',] },
                           68: { 'name':'ARUS', 'p4_path_list':['//QA/READYAPI/Projects/ARUS/',] },
                           70: { 'name':'COFO', 'p4_path_list':['//QA/READYAPI/Projects/COFO/',] },
                           14: { 'name':'Customer Care - CRM', 'p4_path_list':['//QA/READYAPI/Projects/CustomerCare/CRM/',] },
                           21: { 'name':'Customer Care - IVR', 'p4_path_list':['//QA/READYAPI/Projects/CustomerCare/IVR/',] },
                           72: { 'name':'Direct Deposit', 'p4_path_list':['//QA/READYAPI/Projects/DirectDeposit/',] },
                           33: { 'name':'GoBank', 'p4_path_list':['//QA/READYAPI/Projects/GoBank',] },
                           15: { 'name':'Green Dot Network', 'p4_path_list':['//QA/READYAPI/Projects/GDN/',] },
                           9: { 'name':'GreenDot', 'p4_path_list':['//QA/READYAPI/Projects/GreenDot/',] },
                           69: { 'name':'MOTX', 'p4_path_list':['//QA/READYAPI/Projects/MOTX/',] },
                           31: { 'name':'Processor', 'p4_path_list':['//QA/READYAPI/Projects/Processor/',] },
                           19: { 'name':'Risk', 'p4_path_list':['//QA/READYAPI/Projects/RISK/',] },
                           26: { 'name':'SOA', 'p4_path_list':['//QA/READYAPI/Projects/Platform/SOA/',] },
                           29: { 'name':'V3', 'p4_path_list':['//QA/READYAPI/Projects/Platform/V3/',] },
                           11: { 'name':'Walmart', 'p4_path_list':['//QA/READYAPI/Projects/Walmart/',] },
                           71: { 'name':'FEAS', 'p4_path_list':['//QA/READYAPI/Projects/SAFE/',] }, 
                           73: { 'name':'EDAT', 'p4_path_list':['//QA/READYAPI/Projects/EDAT/',] },  
                           76: { 'name':'FireWire', 'p4_path_list':['//QA/READYAPI/Projects/FireWire/',] },
                           78: { 'name':'TPG', 'p4_path_list':['//QA/READYAPI/Projects/TPG/',] },
                           82: { 'name':'RUSH', 'p4_path_list':['//QA/READYAPI/Projects/RUSH/',] },
                           85: { 'name':'BaaS', 'p4_path_list':['//QA/READYAPI/Projects/BaaS/',] },
                           86: { 'name':'GSS', 'p4_path_list':['//QA/READYAPI/Projects/GSS/',] },
                           87: { 'name':'BUX', 'p4_path_list':['//QA/READYAPI/Projects/BUX/',] },                                                                         
                          }
# EXPORT EXCEL SAVE PATH
## User's home directory (e.g., Windows: 'C:/Users/foo/'; Linux: '~/')
_EXPORT_SAVE_DIR = os.path.expanduser('~')
_EXPORT_SAVE_FILENAME = 'TestRail_Unused_Case_log.xlsx'
_EXPORT_SAVE_PATH = os.path.normpath('{0}/{1}'.format(_EXPORT_SAVE_DIR, _EXPORT_SAVE_FILENAME))

if not os.path.exists(_EXPORT_SAVE_DIR):
    warnings.warn('Path {0} not found; will not be able to export Excel spreadsheet'.format(_EXPORT_SAVE_PATH), RuntimeWarning)

class CaseView(View):
    project_id = None
    suite_ids = None
    _template = 'case_report.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """ See decorators;
            if user is not part of _VALID_USERNAMES, they will be
            redirected to the login page.
        """
        return super().dispatch(request, *args, **kwargs)
       
    def get(self, request) -> HttpResponse:
        """ Processes requests from /testrail_report/.
            ReportView.get is the return value of ReportView.as_view().
        """
        if request.is_ajax():
            context = CaseView._process_ajax_request(request)
            return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            context = {'projects': getActiveProjects(request)}
            return render(request, CaseView._template, context=context)
        
        
    def post(self, request):
        # after 'Generate' button is clicked
        if {'project', 'X-Progress-ID'} <= set(request.POST):
            if 'suite' in request.POST:
                suite_ids = request.POST.getlist('suite')
            else:
                suite_ids = []
            project_id = request.POST['project']
            p4_path_list = get_p4_path(int(project_id))
            progress_id = request.POST['X-Progress-ID']
            progress_id_int = int(project_id)
            cases = []
            needCancel = False
            is_all_cases_str = request.POST.get('allcases','N/A')
            is_all_cases = True if is_all_cases_str == 'on' else False
            context =  {'cases' : cases, 'is_canceled' : needCancel}
            if not p4_path_list and not is_all_cases:
                errorMsg = 'There is no p4 path binded with this TestRail Project ' + testrail_util.project_name(progress_id_int) + ', please contact QA-Architecture@greendotcorp.com.'
                messages.add_message(request, messages.ERROR, errorMsg)
                return HttpResponse(json.dumps(context), content_type='application/json')
            try:
                cases, needCancel = getCaseReport(project_id, p4_path_list, progress_id, suite_ids, is_all_cases)
            except Exception as e:
                Logger.log("Failed to get Case Report due to " + str(e))
           
            if not needCancel:
                export.export_xlsx(_EXPORT_SAVE_PATH, testrail_util.project_name(progress_id_int), cases)
            context =  {'cases' : cases, 'is_canceled' : needCancel, 'projects': getActiveProjects(request)}
            return render(request, 'case_report.html', context)
        
#             return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            raise NotImplementedError('/testrail_report/ unsupported post data')
        
        
    @classmethod
    def _process_ajax_request(cls, request) -> dict:
        """ Builds and returns a 'context' dict,
            to be serialized and then processed as an HttpResponse.
        """      
        if 'project_id' in request.GET and not 'is_generate' in request.GET:
            project_id = int(request.GET['project_id'])            
            context = {'suites': Django_Util.convert_to_data_provider(testrail_util.get_suites(project_id))}        
        else:
            raise Http404('unexpected AJAX response received:\n  {0}'.format(request.GET))
        
        return context
    
    
    @classmethod
    def reset(cls) -> None:
        """ Clears saved project_id and suite_ids """
        cls.project_id = None
        cls.suite_ids = None
def _getProjectsMap(request):   
    available_projects = testrail_util.get_projects_by_email(request.user.email)
    projects = (dict((k, available_projects[k]) for k in _TR_PROJECT_P4_MAPPING.keys()) if available_projects else {})
    if projects:
        projects = OrderedDict(sorted(projects.items(), key=lambda x:x[1]))    
    return   projects
def getActiveProjects(request):
    user_projects = testrail_util.get_projects_by_email(request.user.email);
    active_projects = testrail_util.get_projects();
    result_map_temp = {};
    for key in user_projects:
        if key not in active_projects:
            continue;  
        if key in _TR_PROJECT_P4_MAPPING and _TR_PROJECT_P4_MAPPING.get(key).get("name") != user_projects.get(key):
            messages.add_message(request, messages.ERROR, _TR_PROJECT_P4_MAPPING.get(key).get("name") + " from default map doesn't match with TestRail " + active_projects.get(key))     
        result_map_temp[key] = user_projects.get(key)        
    if len(result_map_temp) > 0:
        return OrderedDict(sorted(result_map_temp.items(), key=lambda x:x[1]))
    else:
        return {}
def get_p4_path(p_id:int) -> [str]:
    return (_TR_PROJECT_P4_MAPPING[p_id]['p4_path_list'] if p_id in _TR_PROJECT_P4_MAPPING else [] )
def is_alive(thread):
    is_alive = False
    try:
        is_alive=thread.is_alive()
    except:
        return False
    else:
        return is_alive
def getCaseReport(project_id:str, root_path_list:[str], progress_id:str, suite_ids:[str], all_cases:[bool]):
    resetNeedCancel(progress_id)

    finderThread = FinderThread(project_id, root_path_list, progress_id, suite_ids, all_cases)
    finderThread.start()

    needCancel = False  
          
    while  is_alive(finderThread) and  cache.get(progress_id) != 100: 
        if isNeedCancel(progress_id) :
            needCancel = True
            finderThread.terminate()
            break;
        else:
            time.sleep(1) 
    try:
        if not needCancel:
            cases = finderThread.getResult()['result']
        else:
            cases = []
    except Exception as e:
        Logger.log("Failed to get result due to " + str(e)) 
        
    return (cases, needCancel)
def isNeedCancel(progress_id):
        if cache.get(progress_id + '_cancel') == True:
            return True
        else:
            return False
def resetNeedCancel(progress_id):
        cache.set(progress_id + '_cancel', False)
        
def getProgress(request):
    context_dict = {}
    x_progress_id = request.GET['X-Progress-ID']
    if x_progress_id:
        progress = cache.get(x_progress_id)
        if progress is None:
            progress = 0
    else:
        progress = 0
    context_dict['progress'] = progress
    json_posts = json.dumps(context_dict)
    return HttpResponse(json_posts, content_type='application/json')   
def cancelProgress(request) -> HttpResponse:
    """
    Cancel the thread with given progress id
    """
    context_dict = {}
    success = False
    x_progress_id = request.GET['X-Progress-ID']
    if x_progress_id:
        cache.set(x_progress_id + '_cancel', True)
        success = True
    context_dict['success'] = success
    json_posts = json.dumps(context_dict)
    return HttpResponse(json_posts, content_type='application/json')

def download_case_report(request) -> HttpResponse:
    """ View for the download page, when "Export Excel" button is clicked.
        Prepares Excel report for download.
    """    
    with open(_EXPORT_SAVE_PATH, mode='rb') as file:
        wrapper = wsgiref.util.FileWrapper(file)
        content_type, encoding = mimetypes.guess_type(_EXPORT_SAVE_PATH)
        
        if content_type is None:
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'      # hardcode for fallback

        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(_EXPORT_SAVE_PATH)
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(_EXPORT_SAVE_FILENAME)
        
        return response



