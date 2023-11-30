
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_dashboard.settings')

import django
django.setup()
from apps.qa_monitor.models import RunStatus, RunResult, MonitorType, Environment

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

def add_monitortype(type):
    monitortype_object = MonitorType.objects.get_or_create(type=type)[0]
    monitortype_object.name = type
    monitortype_object.save()
    return monitortype_object
def add_environment(name):
    environment_object = Environment.objects.get_or_create(name=name)[0]
    environment_object.name=name
    environment_object.save()
    return environment_object
def populate():
    add_runstatus(name="Canceled")
    add_runstatus(name="Running")
    add_runstatus(name="Finished")

    add_runresult(name="N/A")
    add_runresult(name="Pass")
    add_runresult(name="Fail")
    
    add_monitortype(type="PAL")
    add_monitortype(type="PIN_GRABBER")
    add_monitortype(type="TSYS_QUEUE")
    
    '''Adding Environment'''
    add_environment(name="DevInt1")
    add_environment(name="DevInt2")
    add_environment(name="QA3")
    add_environment(name="QA4")
    add_environment(name="QA5")
    add_environment(name="Production")

if __name__ == '__main__':
    print ("Starting Monitor Metadata population script...")
    populate()
    print ("Done!!")