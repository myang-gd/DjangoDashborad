import time
from datetime import timedelta

import pyodbc


class TestRailDatabase(object):
    def execute_query(self, query):
        conn_string = 'Driver={SQL Server Native Client 11.0};Server=gdcqatestrail01;' \
                      'Database=testrail_db;uid=auto_reader;pwd=@utoMated34GD!;'

        data = []
        SQL_ATTR_CONNECTION_TIMEOUT = 113
        login_timeout = 60
        connection_timeout = 180
        with pyodbc.connect(conn_string, timeout=login_timeout,
                            attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}) as conn:
            cursor = conn.cursor()
            # print(query)
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                data.append({columns[i]: row[i] for i in range(len(columns))})
        return data

    def generate_case_query(self, stories, start_at, case_count):
        sql = ""
        if start_at < len(stories):
            sql = "SELECT A.id, A.section_id, A.title,B.id suite_id, B.name suite_name, " \
                  "C.id project_id, C.name project_name,A.custom_jira_references, " \
                  "(case isnull(A.custom_automation_type,0) when 0  then 'NotAuto' " \
                  "when 1 then 'CantAuto' else 'Auto' end) AutoType " \
                  " FROM testrail_db.[dbo].[cases] A " \
                  " JOIN testrail_db.[dbo].suites B ON A.suite_id = B.id " \
                  " JOIN testrail_db.[dbo].projects C ON B.project_id = C.id " \
                  " WHERE ("

            first_add = True
            for case_item in stories[start_at:case_count]:
                if first_add:
                    sql = sql + "CHARINDEX('%s',A.custom_jira_references )>0 " % case_item
                    first_add = False
                else:
                    sql = sql + "OR CHARINDEX('%s',A.custom_jira_references )>0 " % case_item
            sql = sql + ") and A.is_copy=0 and B.is_copy=0 and B.is_completed=0 and C.is_completed=0"
        return sql

    def story_2_case(self, related_cases):
        s_2_c = {}
        for item in related_cases:
            refs = item['custom_jira_references'].split(',')
            for jira_id in refs:
                if jira_id.strip() in s_2_c:
                    s_2_c[jira_id.strip()].append(item)
                else:
                    s_2_c[jira_id.strip()] = []
                    s_2_c[jira_id.strip()].append(item)
        return s_2_c

    def get_cases(self, stories):
        related_cases = []
        start_at = 0
        page_count = 25
        while True:
            sql = self.generate_case_query(stories, start_at, start_at + page_count)
            data = self.execute_query(sql)
            for item in data:
                if item['id'] not in [x['id'] for x in related_cases]:
                    related_cases.append(item)
            if start_at + page_count >= len(stories):
                break
            else:
                start_at = start_at + page_count

        return related_cases

    def generate_test_query(self, cases, start_at, case_count):
        sql = ""
        if start_at < len(cases):
            sql = "SELECT TOP 100 A.id, A.section_id, A.title,B.id suite_id, B.name suite_name, " \
                  "C.id project_id, C.name project_name,D.id test_id, D.run_id, E.name status_name " \
                  "FROM testrail_db.[dbo].[cases] A " \
                  "JOIN testrail_db.[dbo].suites B ON A.suite_id = B.id " \
                  "JOIN testrail_db.[dbo].projects C ON B.project_id = C.id " \
                  "JOIN testrail_db.[dbo].tests D ON A.id = D.case_id " \
                  "JOIN testrail_db.[dbo].statuses E ON D.status_id = E.id " \
                  "WHERE A.id in ("
            first_add = True
            for case_item in cases[start_at:case_count]:
                if first_add:
                    sql = sql + str(case_item['id'])
                    first_add = False
                else:
                    sql = sql + ",%s " % str(case_item['id'])
            sql = sql + ") and A.is_copy=0 and B.is_copy=0 and B.is_completed=0 " \
                        "and C.is_completed=0 and D.is_selected =1 order by D.id desc"
        return sql

    def case_2_test(self, related_tests):
        s_2_c = {}
        for item in related_tests:
            if item['id'] in s_2_c:
                s_2_c[item['id']].append(item)
            else:
                s_2_c[item['id']] = []
                s_2_c[item['id']].append(item)
        return s_2_c

    def get_tests(self, cases):
        related_tests = []
        start_at = 0
        page_count = 25
        while True:
            sql = self.generate_test_query(cases, start_at, start_at + page_count)

            data = self.execute_query(sql)
            for item in data:
                if item['test_id'] not in [x['test_id'] for x in related_tests]:
                    related_tests.append(item)
            if start_at + page_count >= len(cases):
                break
            else:
                start_at = start_at + page_count

        return related_tests

    def get_case_per_story(self, stories):
        related_cases = self.get_cases(stories)
        story_2_case = self.story_2_case(related_cases)
        return story_2_case

    def get_case_test_relations(self, stories):
        related_cases = self.get_cases(stories)
        story_2_case = self.story_2_case(related_cases)
        case_2_test = []
        # if len(story_2_case) > 0:
        #     related_tests = self.get_tests(related_cases)
        #     case_2_test = self.case_2_test(related_tests)
        return [story_2_case, case_2_test]

    def generate_plan_summary_query(self, plan_ids, start_at, plan_count):
        sql = ""
        if start_at < len(plan_ids):
            sql = "select A.plan_id, E.name plan_name,D.name project_name, " \
                  "C.id status_id, C.name status_name, count(*) test_count " \
                  "from runs A " \
                  "join tests B on A.id = B.run_id " \
                  "join statuses C on C.id = B.status_id " \
                  "join projects D on D.id = A.project_id " \
                  "join runs E on A.plan_id = E.id " \
                  "where A.plan_id in ("
            first_add = True
            for plan_item in plan_ids[start_at:plan_count]:
                if first_add:
                    sql = sql + str(plan_item)
                    first_add = False
                else:
                    sql = sql + ",%s " % str(plan_item)
            sql = sql + ") AND B.is_selected = 1 " \
                        " group by A.plan_id, E.name, D.name, C.id, C.name "
        return sql

    def generate_plan_failed_summary_query(self, plan_ids, start_at, plan_count):
        sql = ""
        if start_at < len(plan_ids):
            sql = "WITH AllResults As (" \
                  "SELECT tsts.is_selected,rs.plan_id, cs.id,tchg.comment result,tchg.defects," \
                  " dateadd(S, tchg.created_on, '1970-01-01') createdate," \
                  "tchg.test_id casechgid,rs.id runid,rs.config,sts.label status, tsts.id testid," \
                  "ROW_NUMBER() OVER (partition by rs.id,cs.id ORDER BY tchg.id desc) RowNumber " \
                  "FROM [testrail_db].[dbo].[test_changes] tchg " \
                  "inner join testrail_db.dbo.tests tsts on tchg.test_id =tsts.id " \
                  "inner join testrail_db.dbo.cases cs on tsts.case_id=cs.id " \
                  "inner join testrail_db.dbo.runs rs on rs.id=tchg.run_id " \
                  "inner join testrail_db.dbo.statuses sts on sts.id = tsts.status_id " \
                  "where rs.plan_id in ("
            first_add = True
            for plan_item in plan_ids[start_at:plan_count]:
                if first_add:
                    sql = sql + str(plan_item)
                    first_add = False
                else:
                    sql = sql + ",%s " % str(plan_item)
            sql = sql + ") and sts.id not in (1,6) and tsts.is_selected=1 ) " \
                        "select distinct plan_id,result,defects from AllResults where RowNumber=1"
        return sql

    def get_plan_summary(self, plans):
        plan_summary = self.get_data_with_sql_and_list(plans, self.generate_plan_summary_query, 25)
        return plan_summary

    def get_plan_failed_summary(self, plans):
        plan_failed_summary = self.get_data_with_sql_and_list(plans, self.generate_plan_failed_summary_query, 25)
        return plan_failed_summary

    def get_release_progress(self, plans):
        plan_summary = self.get_plan_summary(plans)
        plan_failed_summary = self.get_plan_failed_summary(plans)

        release_progress = {}
        for item in plan_summary:
            status_name = 'fail'
            if item['status_id'] == 1 or item['status_id'] == 6:
                status_name = 'pass'
            if item['status_id'] == 3:
                status_name = 'untested'
            if item['plan_id'] not in release_progress.keys():
                release_progress[item['plan_id']] = {'plan_name': item['plan_name'],
                                                     status_name: item['test_count']}
            else:
                if status_name in release_progress[item['plan_id']].keys():
                    release_progress[item['plan_id']][status_name] += item['test_count']
                else:
                    release_progress[item['plan_id']][status_name] = item['test_count']

        for item in plan_failed_summary:
            if 'failures' not in release_progress[item['plan_id']].keys():
                release_progress[item['plan_id']]['failures'] = \
                    [{'comment': item['result'], 'defects': item['defects']}]
            else:
                release_progress[item['plan_id']]['failures'].append(
                    {'comment': item['result'], 'defects': item['defects']})

        return release_progress

    def generate_coverage_query(self, projects, start_at, case_count):
        sql = ""
        if start_at < len(projects):
            sql = "select P.name ProjectName,R.name SuiteName," \
                  " (case isnull(C.custom_automation_type,0) when 8 then 'Automated_NUnit' " \
                  " when 7 then 'Automated_QuerySurge' " \
                  " when 5 then 'Automated_SeeTest' " \
                  " when 3 then 'Automated_SoapUI' " \
                  "  when 1 then 'CantAuto' else (" \
                  " case when LEN(RTRIM(LTRIM(isnull(C.custom_cucumber_jvm,''))))>0 then 'Automated_JVM' " \
                  " when LEN(RTRIM(LTRIM(isnull(C.custom_cucumber,''))))>0 then 'Automated_Ruby' " \
                  " else 'NotAuto' end) end) AutoType, " \
                  " (case when C.priority_id>=4 then 'P4,5' else 'P3,2,1' end) as Priority, COUNT(1) cal " \
                  " from dbo.suites R WITH (NOLOCK)　" \
                  " JOIN dbo.projects P WITH (NOLOCK)　ON R.project_id = P.id" \
                  " JOIN dbo.cases C WITH (NOLOCK)　ON C.suite_id = R.id and C.is_copy = 0 " \
                  " where P.id in ("
            first_add = True
            for case_item in projects[start_at:case_count]:
                if first_add:
                    sql = sql + str(case_item)
                    first_add = False
                else:
                    sql = sql + ",%s " % str(case_item)
            sql = sql + ") and C.priority_id >0  and CHARINDEX('-Deprecated!',R.name)<=0 " \
                        " and CHARINDEX('-Archived!',R.name)<=0" \
                        " group by P.name, R.name , (case isnull(C.custom_automation_type,0) " \
                        " when 8 then 'Automated_NUnit' when 7 then 'Automated_QuerySurge' " \
                        " when 5 then 'Automated_SeeTest' when 3 then 'Automated_SoapUI' " \
                        " when 1 then 'CantAuto' else ( " \
                        " case when LEN(RTRIM(LTRIM(isnull(C.custom_cucumber_jvm,''))))>0 then 'Automated_JVM'  " \
                        " when LEN(RTRIM(LTRIM(isnull(C.custom_cucumber,''))))>0 then 'Automated_Ruby' " \
                        " else 'NotAuto' end) end), (case when C.priority_id>=4 then 'P4,5' else 'P3,2,1' end)" \
                        " order by P.name,R.name "
        return sql

    def generate_coverage_query_sim(self, projects, start_at, case_count):
        sql = ""
        if start_at < len(projects):
            sql = "select P.id ProjectId,P.name ProjectName,R.id SuiteId,R.name SuiteName," \
                  " (case isnull(C.custom_automation_type,0) when 0 " \
                  " then 'NotAuto' when 1 then 'CantAuto' else 'Auto' end) AutoType, " \
                  " (case when D.priority>=5 then 'P4,5' else 'P3,2,1' end) as Priority, COUNT(1) cal " \
                  " from dbo.suites R WITH (NOLOCK)" \
                  " JOIN dbo.projects P WITH (NOLOCK) ON R.project_id = P.id" \
                  " JOIN dbo.cases C WITH (NOLOCK) ON C.suite_id = R.id and C.is_copy = 0 " \
                  " JOIN dbo.priorities D WITH (NOLOCK) ON D.id = C.priority_id  " \
                  " where P.id in ("
            first_add = True
            for case_item in projects[start_at:case_count]:
                if first_add:
                    sql = sql + str(case_item)
                    first_add = False
                else:
                    sql = sql + ",%s " % str(case_item)
            sql = sql + ") and D.priority >1  and CHARINDEX('Deprecated!',R.name)<=0 " \
                        " and CHARINDEX('Archived!',R.name)<=0 " \
                        " group by P.id,P.name, R.id,R.name , (case isnull(C.custom_automation_type,0) when 0 " \
                        " then 'NotAuto' when 1 then 'CantAuto' else 'Auto' end)," \
                        " (case when D.priority>=5 then 'P4,5' else 'P3,2,1' end)" \
                        " order by P.name,R.id,R.name "
        return sql

    def get_testrail_project(self):
        project_sql = "SELECT [id],[name] FROM [dbo].[projects] WITH (NOLOCK) " \
                      "where id <>35 and is_completed=0 order by name"
        data = self.execute_query(project_sql)
        return data

    def get_data_with_sql_and_list(self, data_lst, query_gen, max_size_each):
        data_get = []
        start_at = 0
        while True:
            sql = query_gen(data_lst, start_at, start_at + max_size_each)
            data = self.execute_query(sql)
            for item in data:
                data_get.append(item)
            if start_at + max_size_each >= len(data_lst):
                break
            else:
                start_at = start_at + max_size_each
        return data_get

    def get_coverage_automation(self, projects):
        coverage = self.get_data_with_sql_and_list(projects, self.generate_coverage_query, 25)
        return coverage

    def get_coverage_automation_sim(self, projects):
        start_time = time.time()
        coverage = self.get_data_with_sql_and_list(projects, self.generate_coverage_query_sim, 25)
        elapsed_time_secs = time.time() - start_time
        print("Execution query took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs)))
        return coverage

# tr = TestRailDatabase()
# ps = [68]
# print(tr.get_coverage_automation_sim(ps))
