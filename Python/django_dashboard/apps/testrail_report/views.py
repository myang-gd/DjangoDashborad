import time
from datetime import timedelta

from django.shortcuts import render
from django.http.response import HttpResponse
from django.http import Http404
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.testrail_report import export
from common_utils import testrail_util
from common_utils.cache_coverage import CacheCoverage
from common_utils.django_util import Django_Util
import json
import mimetypes
import os.path
import warnings
import wsgiref.util
from common_utils.extend_views_database import ExtendViewsDatabase
from common_utils.testrail_database import TestRailDatabase

from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

# ----------------------------------
# USERS WHO HAVE ACCESS
_VALID_USERNAMES = ('tgupta',
                    'zbasmajian',
                    'rbuddaraju',
                    'kngo',
                    'dcasas',
                    'xxie',
                    'liwenchen',
                    'zli',
                    'mzhao')
_VALID_USERNAMES = {name.lower() for name in _VALID_USERNAMES}

# AUTOMATION TYPE MAPPINGS AS LISTED IN TESTRAIL
_NO_AUTOMATION_TYPE = 'None'
_AUTOMATION_TYPE_MAPPING = {None: _NO_AUTOMATION_TYPE,
                            1: "Can't Automate",
                            2: 'Cucumber',
                            3: 'SoapUI',
                            4: 'Specflow',
                            5: 'SeeTest'}

# CASE FIELD MACROS
CUST_AUTO_TYPE = 'custom_automation_type'

# EXPORT EXCEL SAVE PATH
## User's home directory (e.g., Windows: 'C:/Users/foo/'; Linux: '~/')
_EXPORT_SAVE_DIR = os.path.expanduser('~')
_EXPORT_SAVE_FILENAME = 'TestRail_Case_log.xlsx'
_EXPORT_SAVE_PATH = os.path.normpath('{0}/{1}'.format(_EXPORT_SAVE_DIR, _EXPORT_SAVE_FILENAME))

if not os.path.exists(_EXPORT_SAVE_DIR):
    warnings.warn('Path {0} not found; will not be able to export Excel spreadsheet'.format(_EXPORT_SAVE_PATH),
                  RuntimeWarning)


#
# ----------------------------------


class ReportView(View):
    project_id = None
    suite_ids = None
    _template = 'testrail_report.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.username.lower() in _VALID_USERNAMES))
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
            context = ReportView._process_ajax_request(request)
            return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            context = {'projects': testrail_util.get_projects_by_email(request.user.email)}
            return render(request, ReportView._template, context=context)

    def post(self, request):
        """ dispatch() should never call this method """
        raise NotImplementedError('/testrail_report/ should write no post data')

    @classmethod
    def _process_ajax_request(cls, request) -> dict:
        """ Builds and returns a 'context' dict,
            to be serialized and then processed as an HttpResponse.
        """
        # after Project is selected
        if 'project_id' in request.GET:
            cls.project_id = int(request.GET['project_id'])
            context = {'suites': Django_Util.convert_to_data_provider(testrail_util.get_suites(cls.project_id))}

        # Used to determine if 'All Fields' checkbox can be enabled or not
        elif 'suite_ids[]' in request.GET:
            cls.suite_ids = request.GET.getlist('suite_ids[]')
            automation_types = testrail_util.parse_suites_for_automation_types(cls.suite_ids, cls.project_id)
            context = {'automation_types': automation_types}

        # after Test Types are selected and 'Generate' button is clicked
        elif 'automation_types[]' in request.GET:
            automation_types = testrail_util.load_automation_types(request.GET.getlist('automation_types[]'))
            cases = testrail_util.generate_cases(cls.suite_ids, cls.project_id, automation_types)

            # Write results to Excel file when a report is generated
            export.export_xlsx(_EXPORT_SAVE_PATH, testrail_util.project_name(cls.project_id), cases)
            context = {'cases': cases}

        else:
            raise Http404('unexpected AJAX response received:\n  {0}'.format(request.GET))

        return context

    @classmethod
    def reset(cls) -> None:
        """ Clears saved project_id and suite_ids """
        cls.project_id = None
        cls.suite_ids = None


def download(request) -> HttpResponse:
    """ View for the download page, when "Export Excel" button is clicked.
        Prepares Excel report for download.
    """
    with open(_EXPORT_SAVE_PATH, mode='rb') as file:
        wrapper = wsgiref.util.FileWrapper(file)
        content_type, encoding = mimetypes.guess_type(_EXPORT_SAVE_PATH)

        if content_type is None:
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # hardcode for fallback

        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(_EXPORT_SAVE_PATH)
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(_EXPORT_SAVE_FILENAME)

        return response


class CoverageView(TemplateView):
    template_name = "coverage_view.html"

    def format_coverage(self, coverage):
        fmt_coverage = []
        current_project = ""
        current_suite = ""
        project_data = None
        suite_data = None

        start_time = time.time()
        for item in coverage:
            if current_project != item['ProjectName']:
                project_data = {"id": item['ProjectId'], "name": "P[%s] %s" % (item['ProjectId'], item['ProjectName']),
                                "P4,5_Auto": 0, "P4,5_NotAuto": 0, "P4,5_CantAuto": 0, "P4,5_Coverage": 0,
                                "P3,2,1_Auto": 0, "P3,2,1_NotAuto": 0, "P3,2,1_CantAuto": 0, "P3,2,1_Coverage": 0,
                                "Coverage": 0, "_children": []}
                fmt_coverage.append(project_data)
                current_project = item['ProjectName']
                current_suite = ""
            if current_suite != item['SuiteName']:
                suite_data = {"id": item['SuiteId'], "name": "S[%s]%s" % (item['SuiteId'], item['SuiteName']),
                              "P4,5_Auto": 0, "P4,5_NotAuto": 0, "P4,5_CantAuto": 0, "P4,5_Coverage": 0,
                              "P3,2,1_Auto": 0, "P3,2,1_NotAuto": 0, "P3,2,1_CantAuto": 0, "P3,2,1_Coverage": 0,
                              "Coverage": 0}
                project_data['_children'].append(suite_data)
                current_suite = item['SuiteName']

            current_name = "%s_%s" % (item['Priority'], item['AutoType'])
            project_data[current_name] += item['cal']
            suite_data[current_name] += item['cal']

        for pj in fmt_coverage:
            p45_sum = pj['P4,5_Auto'] + pj['P4,5_NotAuto']
            if p45_sum > 0:
                pj['P4,5_Coverage'] = round(pj['P4,5_Auto'] / p45_sum * 100, 2)
            p123_sum = pj['P3,2,1_Auto'] + pj['P3,2,1_NotAuto']
            if p123_sum > 0:
                pj['P3,2,1_Coverage'] = round(pj['P3,2,1_Auto'] / p123_sum * 100, 2)
            if p45_sum + p123_sum > 0:
                pj['Coverage'] = round((pj['P3,2,1_Auto'] + pj['P4,5_Auto']) / (p123_sum + p45_sum) * 100, 2)
            for child in pj['_children']:
                p45_sum = child['P4,5_Auto'] + child['P4,5_NotAuto']
                if p45_sum > 0:
                    child['P4,5_Coverage'] = round(child['P4,5_Auto'] / p45_sum * 100, 2)
                p123_sum = child['P3,2,1_Auto'] + child['P3,2,1_NotAuto']
                if p123_sum > 0:
                    child['P3,2,1_Coverage'] = round(child['P3,2,1_Auto'] / p123_sum * 100, 2)
                if p45_sum + p123_sum > 0:
                    child['Coverage'] = round((child['P3,2,1_Auto'] + child['P4,5_Auto']) / (p123_sum + p45_sum) * 100,
                                              2)

        elapsed_time_secs = time.time() - start_time
        print("Formatting took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs)))

        return fmt_coverage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tr = TestRailDatabase()
        context['projects'] = tr.get_testrail_project()
        projects = self.request.GET.getlist('selectedProjects', [])
        is_spec = False
        if self.request.GET.get('is_spec', 'off') == 'on':
            is_spec = True
        is_lm = False
        if self.request.GET.get('is_lm', 'off') == 'on':
            is_lm = True

        context['is_spec'] = is_spec
        context['is_lm'] = is_lm
        if len(projects) > 0:
            context['selected_projects'] = [int(i) for i in projects]
        else:
            context['selected_projects'] = []

        coverage_provide = tr
        pd_type = self.request.GET.get('coverage_provide', 'extract_sql')
        if pd_type == 'memcached_pd':
            coverage_provide = CacheCoverage()
        elif pd_type == 'extract_sql':
            coverage_provide = ExtendViewsDatabase()

        if len(projects) > 0:
            context['coverage'] = json.dumps(
                self.format_coverage(coverage_provide.get_coverage_automation_sim(projects,
                                                                                  is_spec=is_spec, is_lm=is_lm)))
        else:
            context['coverage'] = []
        return context


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def confluence_using_coverage(request):
    if request.method == 'GET':
        projects = request.GET.get('projects', r'')
        groups = request.GET.get('groups', r'')
        suites = request.GET.get('suites', r'')
        excludeSuites = request.GET.get('exclude_suites', r'')
        is_spec = request.GET.get('is_spec', r'false').lower() == 'true' \
                  or request.GET.get('is_spec', r'false').lower() == "on" \
                  or request.GET.get('regression', r'false').lower() == 'true'
        is_lm = (request.GET.get('latestMilestone', r'false').lower() == 'true'
                 or request.GET.get('latestMilestone', r'false').lower() == "on") \
                or (request.GET.get('lastestMilestone', r'false').lower() == 'true'
                    or request.GET.get('lastestMilestone', r'false').lower() == "on")
        is_sub_sections = request.GET.get('include_subgroups', r'true').lower() == 'true'
        priority = request.GET.get('priority', r'')

        if projects:
            projects_int = [int(i) for i in projects.split(",")]
        else:
            return Response({"Error": "projects should not be empty, please input as : coverage_api/?projects=1,2,3"})

        suites_int = []
        if suites:
            suites_int = [int(i) for i in suites.split(",")]

        if excludeSuites:
            suites_int = [int(i) for i in excludeSuites.split(",")]
            suites_int.insert(0, -1)

        groups_int = []
        if groups:
            groups_int = [int(i) for i in groups.split(",")]

        coverage = ExtendViewsDatabase().get_coverage_condition(projects_int, suites_int, groups_int,
                                                                is_spec, is_lm, is_sub_sections, priority)
        return Response(coverage)
