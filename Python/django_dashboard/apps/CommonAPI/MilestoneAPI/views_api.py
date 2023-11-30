from rest_framework.views import APIView
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from . import utils


PROJECT_NAME = 'project_name'
BASE_LINE_DATE = 'base_line_date'
MILESTONE = 'milestone'
SPRINT_DATE = 'sprint_date'
SPRINT1_DATE = 'sprint1_date'
SPRINT2_DATE = 'sprint2_date'
HARDENING_DATE = 'hardening_date'
PIE_DATE = 'pie_date'
RELEASE_DATE = 'release_date'
SPRINT_STATE = 'sprint_state'
MILESTONE_LIST = 'milestone_list'

class CurrentSprintDetail(APIView):
    #get method to get current sprint details
    def get(self, request, format=None):
        error_response, responseData = self.get_current_sprint_info(request)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CurrentSprintDetailSerializer(responseData, many=False)
        return Response(serializer.data)
    
    def get_current_sprint_info(self, request):
        error_response = None
        responseData = {}
        data = request.GET
        project_name = data.get(serializers.PROJECT_NAME)
        base_line_date = utils.MilestoneUtils.dateTimeParser(data.get(serializers.BASE_LINE_DATE))
        sql_query = "select top 1 * from [automation].[dbo].[JiraMilestone] where '{0}' <= ReleaseDate and ProjectName='{1}' order by ReleaseDate".format(utils.MilestoneUtils.dateTimeFormater(base_line_date), project_name)
        if project_name.strip() == 'CRM':
            sql_query = "select top 1 * from [automation].[dbo].[JiraMilestone] where '{0}' < ReleaseDate and ProjectName='{1}' order by ReleaseDate".format(utils.MilestoneUtils.dateTimeFormater(base_line_date), project_name)
        result_records = utils.MilestoneUtils().dbQuery(sql_query)
        responseData[BASE_LINE_DATE] = base_line_date
        responseData[PROJECT_NAME] = result_records[0]['ProjectName'].strip()
        responseData[MILESTONE] = result_records[0]['Milestone'].strip()
        responseData[SPRINT_DATE] = result_records[0]['SprintDate']
        responseData[SPRINT1_DATE] = result_records[0]['Sprint1Date']
        responseData[SPRINT2_DATE] = result_records[0]['Sprint2Date']
        responseData[HARDENING_DATE] = result_records[0]['HardeningDate']
        responseData[PIE_DATE] = result_records[0]['PIEDate']
        responseData[RELEASE_DATE] = result_records[0]['ReleaseDate']
        if project_name.strip() == 'CRM':
            if datetime.date(base_line_date) >= datetime.date(result_records[0]['Sprint1Date']) and datetime.date(base_line_date) < datetime.date(result_records[0]['Sprint2Date']):
                responseData[SPRINT_STATE] = 'Sprint 1'
            if datetime.date(base_line_date) >= datetime.date(result_records[0]['Sprint2Date']) and datetime.date(base_line_date) < datetime.date(result_records[0]['HardeningDate']):
                responseData[SPRINT_STATE] = 'Sprint 2'
            if datetime.date(base_line_date) >= datetime.date(result_records[0]['HardeningDate']) and datetime.date(base_line_date) < datetime.date(result_records[0]['ReleaseDate']):
                responseData[SPRINT_STATE] = 'Hardening'
        return error_response, responseData

class SpecificSprintInfo(APIView):
    #get method to get specific sprint details
    def get(self, request, format=None):
        error_response, responseData = self.get_specific_sprint_info(request)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.SpecificSprintInfoSerializer(responseData, many=False)
        return Response(serializer.data)
    
    def get_specific_sprint_info(self, request):
        error_response = None
        responseData = {}
        data = request.GET
        project_name = data.get(serializers.PROJECT_NAME)
        milestone = data.get(serializers.MILESTONE)
        sql_query = "select * from [automation].[dbo].[JiraMilestone] where ProjectName='{0}' and Milestone='{1}'".format(project_name, milestone)
        result_records = utils.MilestoneUtils().dbQuery(sql_query)
        responseData[PROJECT_NAME] = result_records[0]['ProjectName'].strip()
        responseData[MILESTONE] = result_records[0]['Milestone'].strip()
        responseData[SPRINT_DATE] = result_records[0]['SprintDate']
        responseData[SPRINT1_DATE] = result_records[0]['Sprint1Date']
        responseData[SPRINT2_DATE] = result_records[0]['Sprint2Date']
        responseData[HARDENING_DATE] = result_records[0]['HardeningDate']
        responseData[PIE_DATE] = result_records[0]['PIEDate']
        responseData[RELEASE_DATE] = result_records[0]['ReleaseDate']
        return error_response, responseData

class ValidSprintListInfo(APIView):
    def get(self, request, format=None):
        error_response, responseData = self.get_valid_sprint_list_info(request)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.SprintListSerializer(responseData, many=False)
        return Response(serializer.data)
    def get_valid_sprint_list_info(self, request):
        error_response = None
        responseData = {}
        res_data = []
        data = request.GET
        project_name = data.get(serializers.PROJECT_NAME)
        base_line_date = utils.MilestoneUtils.dateTimeParser(data.get(serializers.BASE_LINE_DATE))
        sql_query = "select * from [automation].[dbo].[JiraMilestone] where '{0}' <= ReleaseDate and ProjectName='{1}' order by ReleaseDate".format(utils.MilestoneUtils.dateTimeFormater(base_line_date), project_name)
        result_records = utils.MilestoneUtils().dbQuery(sql_query)
        responseData[PROJECT_NAME] = project_name
        responseData[BASE_LINE_DATE] = base_line_date
        for i in range(len(result_records)):
            tmp_Data = {}
            tmp_Data[MILESTONE] = result_records[i]['Milestone'].strip()
            tmp_Data[SPRINT_DATE] = result_records[i]['SprintDate']
            tmp_Data[SPRINT1_DATE] = result_records[i]['Sprint1Date']
            tmp_Data[SPRINT2_DATE] = result_records[i]['Sprint2Date']
            tmp_Data[HARDENING_DATE] = result_records[i]['HardeningDate']
            tmp_Data[PIE_DATE] = result_records[i]['PIEDate']
            tmp_Data[RELEASE_DATE] = result_records[i]['ReleaseDate']            
            res_data.append(tmp_Data)
        responseData[MILESTONE_LIST] = res_data
        return error_response, responseData