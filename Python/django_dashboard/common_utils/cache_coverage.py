from django.core.cache import cache
import time

from common_utils.testrail_database import TestRailDatabase


class CacheCoverage(object):
    expired = 60 * 60 * 12
    testrail = TestRailDatabase()

    def get_coverage_automation_sim(self, projects):
        coverage = []
        for prj in projects:
            prj_key = "tr_prj_%s" % prj
            prj_data = cache.get(prj_key)
            if not prj_data:
                coverage_data = self.testrail.get_coverage_automation_sim([prj])
                cache.set(prj_key, coverage_data, self.expired)
            else:
                print("======Get Coverage Data From Cache For Project : %s" % prj)
            if cache.get(prj_key) is not None:
                coverage.extend(cache.get(prj_key))

        return coverage

    def warm_up_coverage(self):
        projects = self.testrail.get_testrail_project()
        for item in projects:
            prj_key = "tr_prj_%s" % item['id']
            prj_data = cache.get(prj_key)
            if not prj_data:
                print("Warm up project : %s :: %s" % (item['id'], item['name']))
                coverage_data = self.testrail.get_coverage_automation_sim([item['id']])
                cache.set(prj_key, coverage_data, self.expired)
