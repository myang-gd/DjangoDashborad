import time
from datetime import timedelta
import queue
import logging

import pyodbc


class ExtendViewsDatabase(object):
    def execute_query(self, query):
        conn_string = 'Driver={SQL Server Native Client 11.0};Server=GDCQAAUTOSQL201;' \
                      'Database=extend_views;uid=qa_automation;pwd=Gr33nDot!;'

        data = []
        SQL_ATTR_CONNECTION_TIMEOUT = 113
        login_timeout = 60
        connection_timeout = 180
        with pyodbc.connect(conn_string, timeout=login_timeout,
                            attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}) as conn:
            cursor = conn.cursor()
            #print(query)
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                data.append({columns[i]: row[i] for i in range(len(columns))})
        return data

    def generate_coverage_query_sim_spec_lm(self, projects, start_at, case_count, suites=[], sections=[], priority=""):
        logger = logging.getLogger("extend_views_database")
        sql = ""
        if start_at < len(projects):
            sql = " SELECT RTRIM(CAST(ProjectId as varchar(10))) ProjectId, RTRIM(ProjectName) ProjectName, " \
                  " RTRIM(CAST(SuiteId as varchar(10))) SuiteId, " \
                  " RTRIM(SuiteName) SuiteName," \
                  " RTRIM(AutoType) AutoType, RTRIM(PriorityName) As Priority, SUM([Count]) as cal" \
                  " FROM [extend_views].[dbo].[AutoCoverageSpecSectionLM] " \
                  " WHERE ProjectId in ("
            if len(projects) > 0:
                sql = sql + ",".join([str(i) for i in projects[start_at:case_count]]) + ") "

            if len(suites) > 0 and suites[0] == -1:
                sql = sql + " AND SuiteId not in (" + ",".join([str(i) for i in suites]) + ") "
            elif len(suites) > 0:
                sql = sql + " AND SuiteId in (" + ",".join([str(i) for i in suites]) + ") "

            if len(sections) > 0:
                sql = sql + " AND SectionId in (" + ",".join([str(i) for i in sections]) + ") "
            if priority:
                if priority == "p45":
                    sql = sql + " AND RTRIM(PriorityName) = 'P4,5' "
                elif priority == "p123":
                    sql = sql + " AND RTRIM(PriorityName) = 'P3,2,1' "

            sql = sql + " GROUP BY ProjectId,ProjectName,SuiteId,SuiteName,AutoType,PriorityName" \
                        " order by ProjectName,SuiteId, SuiteName "
            logger.info(sql)
        return sql

    def generate_coverage_query_sim_spec(self, projects, start_at, case_count, suites=[], sections=[], priority=""):
        logger = logging.getLogger("extend_views_database")
        sql = ""
        if start_at < len(projects):
            sql = " SELECT RTRIM(CAST(ProjectId as varchar(10))) ProjectId, RTRIM(ProjectName) ProjectName, " \
                  " RTRIM(CAST(SuiteId as varchar(10))) SuiteId, " \
                  " RTRIM(SuiteName) SuiteName," \
                  " RTRIM(AutoType) AutoType, RTRIM(PriorityName) As Priority, SUM([Count]) as cal" \
                  " FROM [extend_views].[dbo].[AutoCoverageSpecSection] " \
                  " WHERE ProjectId in ("
            if len(projects) > 0:
                sql = sql + ",".join([str(i) for i in projects[start_at:case_count]]) + ") "

            if len(suites) > 0 and suites[0] == -1:
                sql = sql + " AND SuiteId not in (" + ",".join([str(i) for i in suites]) + ") "
            elif len(suites) > 0:
                sql = sql + " AND SuiteId in (" + ",".join([str(i) for i in suites]) + ") "

            if len(sections) > 0:
                sql = sql + " AND SectionId in (" + ",".join([str(i) for i in sections]) + ") "
            if priority:
                if priority == "p45":
                    sql = sql + " AND RTRIM(PriorityName) = 'P4,5' "
                elif priority == "p123":
                    sql = sql + " AND RTRIM(PriorityName) = 'P3,2,1' "
            sql = sql + " GROUP BY ProjectId,ProjectName,SuiteId,SuiteName,AutoType,PriorityName" \
                        " order by ProjectName,SuiteId, SuiteName "
            logger.info(sql)
        return sql

    def generate_coverage_query_sim(self, projects, start_at, case_count, suites=[], sections=[], priority=""):
        logger = logging.getLogger("extend_views_database")
        sql = ""
        if start_at < len(projects):
            sql = " SELECT RTRIM(CAST(ProjectId as varchar(10))) ProjectId, RTRIM(ProjectName) ProjectName, " \
                  " RTRIM(CAST(SuiteId as varchar(10))) SuiteId, " \
                  " RTRIM(SuiteName) SuiteName," \
                  " RTRIM(AutoType) AutoType, RTRIM(PriorityName) As Priority, SUM([Count]) as cal" \
                  " FROM [extend_views].[dbo].[AutoCoverageSection] " \
                  " WHERE ProjectId in ("
            if len(projects) > 0:
                sql = sql + ",".join([str(i) for i in projects[start_at:case_count]]) + ") "

            if len(suites) > 0 and suites[0] == -1:
                sql = sql + " AND SuiteId not in (" + ",".join([str(i) for i in suites]) + ") "
            elif len(suites) > 0:
                sql = sql + " AND SuiteId in (" + ",".join([str(i) for i in suites]) + ") "

            if len(sections) > 0:
                sql = sql + " AND SectionId in (" + ",".join([str(i) for i in sections]) + ") "
            if priority:
                if priority == "p45":
                    sql = sql + " AND RTRIM(PriorityName) = 'P4,5' "
                elif priority == "p123":
                    sql = sql + " AND RTRIM(PriorityName) = 'P3,2,1' "
            sql = sql + " GROUP BY ProjectId,ProjectName,SuiteId,SuiteName,AutoType,PriorityName" \
                        " order by ProjectName,SuiteId, SuiteName "
            logger.info(sql)
        return sql

    def generate_coverage_query_sim_lm(self, projects, start_at, case_count, suites=[], sections=[], priority=""):
        logger = logging.getLogger("extend_views_database")
        sql = ""
        if start_at < len(projects):
            sql = " SELECT RTRIM(CAST(ProjectId as varchar(10))) ProjectId, RTRIM(ProjectName) ProjectName, " \
                  " RTRIM(CAST(SuiteId as varchar(10))) SuiteId, " \
                  " RTRIM(SuiteName) SuiteName," \
                  " RTRIM(AutoType) AutoType, RTRIM(PriorityName) As Priority, SUM([Count]) as cal" \
                  " FROM [extend_views].[dbo].[AutoCoverageSectionLM] " \
                  " WHERE ProjectId in ("
            if len(projects) > 0:
                sql = sql + ",".join([str(i) for i in projects[start_at:case_count]]) + ") "

            if len(suites) > 0 and suites[0] == -1:
                sql = sql + " AND SuiteId not in (" + ",".join([str(i) for i in suites]) + ") "
            elif len(suites) > 0:
                sql = sql + " AND SuiteId in (" + ",".join([str(i) for i in suites]) + ") "

            if len(sections) > 0:
                sql = sql + " AND SectionId in (" + ",".join([str(i) for i in sections]) + ") "
            if priority:
                if priority == "p45":
                    sql = sql + " AND RTRIM(PriorityName) = 'P4,5' "
                elif priority == "p123":
                    sql = sql + " AND RTRIM(PriorityName) = 'P3,2,1' "
            sql = sql + " GROUP BY ProjectId,ProjectName,SuiteId,SuiteName,AutoType,PriorityName" \
                        " order by ProjectName,SuiteId, SuiteName "
            logger.info(sql)
        return sql

    def get_data_with_sql_and_list(self, data_lst, query_gen, max_size_each, suites=[], sections=[], priority=""):
        data_get = []
        start_at = 0
        while True:
            sql = query_gen(data_lst, start_at, start_at + max_size_each, suites, sections, priority)
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

    def get_coverage_automation_sim(self, projects, is_spec=False, is_lm=False, suites=[], sections=[], priority=""):
        start_time = time.time()
        if is_spec:
            if is_lm:
                coverage = self.get_data_with_sql_and_list(projects, self.generate_coverage_query_sim_spec_lm, 25,
                                                           suites, sections, priority)
            else:
                coverage = self.get_data_with_sql_and_list(projects, self.generate_coverage_query_sim_spec, 25, suites,
                                                           sections, priority)
        else:
            if is_lm:
                coverage = self.get_data_with_sql_and_list(projects, self.generate_coverage_query_sim_lm, 25, suites,
                                                           sections, priority)
            else:
                coverage = self.get_data_with_sql_and_list(projects, self.generate_coverage_query_sim, 25, suites,
                                                           sections, priority)

        elapsed_time_secs = time.time() - start_time
        print("Execution query took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs)))
        return coverage

    def get_coverage_condition(self, projects, suites, sections, is_spec, is_latest_milestone, is_sub_sections, priority):
        if is_sub_sections:
            sections_all_sub = self.get_sub_setcions(sections)
        else:
            sections_all_sub = sections
        coverage = self.get_coverage_automation_sim(projects, is_spec, is_latest_milestone, suites, sections_all_sub, priority)
        confluence_coverage = {"projects": projects, "suites": suites, "groups": sections_all_sub, "total_coverage": 0,
                               "is_current_release": is_latest_milestone, "is_spec": is_spec, "priority": priority}
        auto_count = 0
        not_auto_count = 0

        for item in coverage:
            if item["AutoType"] == 'Auto':
                auto_count = auto_count + item["cal"]
            elif item["AutoType"] == 'NotAuto':
                not_auto_count = not_auto_count + item["cal"]

        if auto_count + not_auto_count > 0:
            confluence_coverage["total_coverage"] = round(auto_count / (auto_count + not_auto_count) * 100, 2)
        return confluence_coverage

    def get_sub_setcions(self, sections):
        sections_ids = []
        section_roots = queue.Queue()
        for item in sections:
            section_roots.put(item)

        while not section_roots.empty():
            id = section_roots.get()
            sections_ids.append(id)

            sql = "SELECT [id],[name] FROM [GDCQATESTRAIL01].[testrail_db].[dbo].[sections] " \
                  "where is_copy=0 and parent_id =" + str(id)
            for item in self.execute_query(sql):
                section_roots.put(item['id'])

        return sections_ids
