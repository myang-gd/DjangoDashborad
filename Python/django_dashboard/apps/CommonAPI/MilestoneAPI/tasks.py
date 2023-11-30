from celery import shared_task
from . import views_confluence
import re
import datetime
from . import utils
from django.conf import settings
from common_utils.io_util import FileUtil

@shared_task
def pushMilestone2DbViaConf(run_context):
    result_map = views_confluence.getContentsFromConf()    
    for project, releases in result_map.items():
        insert_sql_query = None
        for release in releases:
            value = None
            milestone = None
            sprint_date = None
            pie_date = None
            sprint1_date = None
            sprint2_date = None
            hardening_date = None
            release_date = None
            for key in release.keys():
                if re.match("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$", release[key]):
                    value = datetime.datetime.strptime(release[key],'%m/%d/%y').strftime('%Y-%m-%d 00:00:00.000')
                if re.match("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$", release[key]):
                    value = datetime.datetime.strptime(release[key],'%m/%d/%Y').strftime('%Y-%m-%d 00:00:00.000')
                if project == 'GBOS' and 'Milestone' in key:
                    milestone = release[key].strip().replace("M", "Milestone ")
                if project == 'MOVE' and 'Milestone' in key:
                    milestone = release[key]
                if project == 'Tax' and re.match("^Milestone$", key):
                    milestone = 'Sprint ' + release[key].strip()
                if project == 'CRM' and 'Release' in key:
                    milestone = 'Release ' + release[key].strip() 
                if 'SprintStart' in key:
                    sprint_date = value
                if 'PIE' in key or 'pie' in key:
                    pie_date = value
                if 'Sprint 1' in key or 'Sprint1' in key:
                    sprint1_date = value
                if 'Sprint 2' in key or 'Sprint2' in key:
                    sprint2_date = value
                if 'Hardening' in key:
                    hardening_date = value
                if 'PROD' in key:
                    release_date = value
            if sprint1_date == None and project == 'CRM':
                continue
            insert_sql_query = {
                    'GBOS': "begin if not exists (select * from [automation].[dbo].[JiraMilestone] where ProjectName='BaaS' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestone] values('BaaS', '{0}', NULL, '{1}', NULL, NULL, NULL, NULL, '{2}', '{3}') end end".format(milestone, sprint_date, pie_date, release_date),
                    'MOVE': "begin if not exists (select * from [automation].[dbo].[JiraMilestone] where ProjectName='FireWire' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestone] values('FireWire', '{0}', NULL, '{1}', NULL, NULL, NULL, NULL, '{2}', '{3}') end end".format(milestone, sprint_date, pie_date, release_date),
                    'Tax': "begin if not exists (select * from [automation].[dbo].[JiraMilestone] where ProjectName='TAX' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestone] values('TAX', '{0}', NULL, '{1}', NULL, NULL, NULL, NULL, '{2}', '{3}') end end".format(milestone, sprint_date, pie_date, release_date),
                    'CRM': "begin if not exists (select * from [automation].[dbo].[JiraMilestone] where ProjectName='CRM' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestone] values('CRM', '{0}', NULL, NULL, '{1}', '{2}', NULL, '{3}', NULL, '{4}') end end".format(milestone, sprint1_date, sprint2_date, hardening_date, release_date)
                }[project]
            FileUtil.appendtoFile('%s\MilestoneAPI_JiraMilestone_table_data.log' % (settings.LOG_ROOT_PATH), insert_sql_query)
            utils.MilestoneUtils().dbInsert(insert_sql_query)
def pushMilestone2DbViaConfPreview(run_context):
    result_map = views_confluence.getContentsFromConf()    
    for project, releases in result_map.items():
        insert_sql_query = None
        for release in releases:
            value = None
            milestone = None
            sprint_date = None
            pie_date = None
            sprint1_date = None
            sprint2_date = None
            hardening_date = None
            release_date = None
            for key in release.keys():
                if re.match("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$", release[key]):
                    value = datetime.datetime.strptime(release[key],'%m/%d/%y').strftime('%Y-%m-%d 00:00:00.000')
                if re.match("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$", release[key]):
                    value = datetime.datetime.strptime(release[key],'%m/%d/%Y').strftime('%Y-%m-%d 00:00:00.000')
                if project == 'GBOS' and 'Milestone' in key:
                    milestone = release[key].strip().replace("M", "Milestone ")
                if project == 'MOVE' and 'Milestone' in key:
                    milestone = release[key]
                if project == 'Tax' and re.match("^Milestone$", key):
                    milestone = 'Sprint ' + release[key].strip()
                if project == 'CRM' and 'Release' in key:
                    milestone = 'Release ' + release[key].strip() 
                if 'SprintStart' in key:
                    sprint_date = value
                if 'PIE' in key or 'pie' in key:
                    pie_date = value
                if 'Sprint 1' in key or 'Sprint1' in key:
                    sprint1_date = value
                if 'Sprint 2' in key or 'Sprint2' in key:
                    sprint2_date = value
                if 'Hardening' in key:
                    hardening_date = value
                if 'PROD' in key:
                    release_date = value
            if sprint1_date == None and project == 'CRM':
                continue
            insert_sql_query = {
                    'GBOS': "begin if not exists (select * from [automation].[dbo].[JiraMilestonePreview] where ProjectName='BaaS' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestonePreview] values('BaaS', '{0}', NULL, '{1}', NULL, NULL, NULL, NULL, '{2}', '{3}') end end".format(milestone, sprint_date, pie_date, release_date),
                    'MOVE': "begin if not exists (select * from [automation].[dbo].[JiraMilestonePreview] where ProjectName='FireWire' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestonePreview] values('FireWire', '{0}', NULL, '{1}', NULL, NULL, NULL, NULL, '{2}', '{3}') end end".format(milestone, sprint_date, pie_date, release_date),
                    'Tax': "begin if not exists (select * from [automation].[dbo].[JiraMilestonePreview] where ProjectName='TAX' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestonePreview] values('TAX', '{0}', NULL, '{1}', NULL, NULL, NULL, NULL, '{2}', '{3}') end end".format(milestone, sprint_date, pie_date, release_date),
                    'CRM': "begin if not exists (select * from [automation].[dbo].[JiraMilestonePreview] where ProjectName='CRM' and Milestone='{0}') begin insert into [automation].[dbo].[JiraMilestonePreview] values('CRM', '{0}', NULL, NULL, '{1}', '{2}', NULL, '{3}', NULL, '{4}') end end".format(milestone, sprint1_date, sprint2_date, hardening_date, release_date)
                }[project]
            FileUtil.appendtoFile('%s\MilestoneAPI_JiraMilestone_table_data.log' % (settings.LOG_ROOT_PATH), insert_sql_query)
            utils.MilestoneUtils().dbInsert(insert_sql_query)