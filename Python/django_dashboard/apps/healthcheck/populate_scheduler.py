'''
Created on Mar 23, 2016

@author: zbasmajian
'''
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_dashboard.settings')

import django
django.setup()

from apps.healthcheck.models import RunStatus, RunResult

def add_runstatus(name):
    runstatus_object = RunStatus.objects.get_or_create(name=name)[0]
    runstatus_object.name=name
    runstatus_object.save()
    return runstatus_object

def add_runresult(name):
    runresult_object = RunResult.objects.get_or_create(name=name)[0]
    runresult_object.name = name
    runresult_object.save()
    return runresult_object

def populate():
    add_runstatus(name="Canceled")
    add_runstatus(name="Running")
    add_runstatus(name="Finished")

    add_runresult(name="N/A")
    add_runresult(name="Pass")
    add_runresult(name="Fail")
    

if __name__ == '__main__':
    print ("Starting Healthcheck Scheduler Metadata population script...")
    populate()
    print ("Done!!")