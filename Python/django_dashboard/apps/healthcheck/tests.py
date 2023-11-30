import os
from django.forms.models import model_to_dict
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_dashboard.settings')

import django
django.setup()

from apps.healthcheck.models import Vip, IndividualServer, Environment, Operation, Service
from collections import OrderedDict

vipList = Vip.objects.all();
environment = Environment.objects.filter(name="QA4")
vip_server_operation_map = OrderedDict()
for vip in vipList:
    operation_list = Operation.objects.filter(environment=environment, vip=vip)
    server_operation_map = {}
    for operation in operation_list:
        operation_fields = model_to_dict(operation, fields=[field.name for field in operation._meta.fields])
        service_object = Service.objects.get(id=operation.service.id)
        service_fields = model_to_dict(service_object, fields=[field.name for field in service_object._meta.fields if field.name != 'name'])
        service_operation_field = operation_fields.copy()
        service_operation_field.update(service_fields)
        serviceName = operation.service.name
        if serviceName in server_operation_map:
            server_operation_map.get(serviceName).append(service_operation_field)
        else:
            server_operation_map[serviceName] = [service_operation_field]
            print(str(server_operation_map))
            
    vip_server_operation_map[vip.vipName] = server_operation_map

print(str(vip_server_operation_map))

'''
environment_list = Environment.objects.all();
vip_list = Vip.objects.all()
individual_server_list = IndividualServer.objects.all()
vip_map = {}
for vip in vip_list:
    vip_map[vip.displayName] = {}
    vip_map[vip.displayName]['vip_name'] = vip.vipName
    vip_map[vip.displayName]['environment_list'] = {}
    for environment in environment_list:
        vip_map[vip.displayName]['environment_list'][environment.name] = []
        for individual_server in individual_server_list:
            if vip.id == individual_server.vip.id and individual_server.environment.id == environment.id: 
                vip_map[vip.displayName]['environment_list'][environment.name].append(individual_server.name)   
   
print(vip_map)


for k, v in vip_map.items():
    for k, v in v.items():
        if type(v) is dict:
            for k, v in v.items():
                print(k)
'''