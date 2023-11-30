from celery import shared_task
from common_utils.network import NetworkUtil
import boto3
import time
import requests
from apps.ConfigModifier import models, views_api, views
from django.db.models import Q
from common_utils.io_util import FileUtil
from django.conf import settings
import traceback

region_name='us-west-2'
service_name = 'ec2'
GREEN_STACK = 'green'
BLUE_STACK = 'blue'
AWS_CM_ENV_MAP = {"PIE":"AWS_PI", "QA":"AWS_QA"}

@shared_task
def processUpdateHost(run_context): 
    Config = [('PIE','BOS', 'COM', [('AWS-PI-BLUE','BOS','COM'),('AWS-PI-GREEN','BOS','COM'),('AWS-PI','BOS','COM')]),
              ('PIE','BOS', 'APP', [('AWS-PI-BLUE','BOS','APP'),('AWS-PI-GREEN','BOS','APP'),('AWS-PI','BOS','APP')]),
			  ('PIE','BOS', 'PRT', [('AWS-PI','BOS','PRT')]),
              ('PIE','BOS', 'PN', [('AWS-PI','BOS','PN')]),
			  ('PIE','BOS', 'RH', [('AWS-PI','BOS','RH'),('AWS-PI-GREEN','BOS','RH')]),
			  ('QA','BOS', 'APP', [('AWS-QA','BOS','APP')]),
              ('QA','BOS', 'COM', [('AWS-QA','BOS','COM')]),
              ('QA','BOS', 'PRT', [('AWS-QA','BOS','PRT')]),
			  ('QA','BOS', 'RH', [('AWS-QA','BOS','RH')]),
			  ('QA','BOS', 'PN', [('AWS-QA','BOS','PN')]),
			  ('QA','BOS', 'OD', [('AWS-QA','BOS','OD')]),
			  ('QA','BOS', 'FP', [('AWS-QA','BOS','FP')]),
              ('PIE','BOS', 'FP', [('AWS-PI','BOS','FP')]),
			  ('QA','BOS', 'CND', [('AWS-QA','BOS','CND')]),
			  ('PIE','BOS', 'OD', [('AWS-PI','BOS','OD')]),
              ('QA','BOS', 'FR', [('AWS-QA','BOS','FR')]),
              ('PIE','BOS', 'FR', [('AWS-PI','BOS','FR')]),
              ('QA','BOS', 'CORE', [('AWS-QA','BOS','CORE')]),
              ('PIE','BOS', 'CORE', [('AWS-PI','BOS','CORE')])
             ]
    
    FileUtil.appendtoFile('%s\configModifier_update_host_service.log' % (settings.LOG_ROOT_PATH), "Start processUpdateHost.")
    colorstack_map = {} 
    for i in Config:
        try:
            env = i[0]
            project = i[1]
            tier = i[2]
            custom_filter = [
                    {
                        'Name': 'tag:Environment',
                        'Values': [env]
                    },
                    {
                        'Name': 'tag:Project',
                        'Values': [project]
                    },
                    {
                        'Name': 'tag:Tier',
                        'Values': [tier]
                    },
                ]
            key_name = env + '_' + project
            if key_name not in colorstack_map:
                colorstack_map[key_name] = getEnvColorStack(env, project)
                if colorstack_map[key_name] == '':
                    raise Exception('Failed to colorstack for ' + key_name)                
                FileUtil.appendtoFile('%s\configModifier_update_host_service.log' % (settings.LOG_ROOT_PATH), 'Color of %s is %s' %(key_name, colorstack_map.get(key_name)))
            session = boto3.Session(profile_name=env.lower())  
            client = session.client(service_name,region_name=region_name)
            for j in i[3]:
                target_env = j[0]
                target_project = j[1]
                target_tier = j[2]          
                instances = client.describe_instances(Filters=custom_filter)['Reservations']
                for server in instances:
                    print(server['Instances'][0]['PrivateDnsName'])
                    print(server['Instances'][0]['PrivateIpAddress'])
                    host_ip = server['Instances'][0]['PrivateIpAddress']
                    server_color = getColorStack(server)
                    if env == 'PIE':
                        if getColorStack(server) == BLUE_STACK and target_env == 'AWS-PI-GREEN':
                            continue
                        if getColorStack(server) == GREEN_STACK and target_env == 'AWS-PI-BLUE':
                            continue
                        if server_color == '':
                            FileUtil.appendtoFile('%s\configModifier_update_host.log' % (settings.LOG_ROOT_PATH), 'Failed to get ColorStack for %s %s %s' %(env, project, tier))
                            continue
                    if key_name in colorstack_map:
                        if server_color != colorstack_map[key_name]:
                            continue
                    found = False
                    server_query = Q(environment_id__environment=target_env,server_type__project__name=target_project,server_type__server_tier__name=target_tier)
                    FileUtil.appendtoFile('%s\configModifier_update_host_service.log' % (settings.LOG_ROOT_PATH), 'Checking server ip %s %s %s AWS ip: %s server color: %s env color: %s' %(target_env, target_project, target_tier, host_ip, server_color, colorstack_map.get(key_name)))
                    if NetworkUtil.check_ping(host_ip) and not models.Servers.objects.filter(Q(server_name=host_ip), server_query).exists():
                        for server in models.Servers.objects.filter(server_query):
                            old_name = server.server_name
                            server.server_name = host_ip
                            server.save()
                            FileUtil.appendtoFile('%s\configModifier_update_host.log' % (settings.LOG_ROOT_PATH), 'Updated server ip %s %s %s from %s to %s server color: %s env color: %s' %(target_env, target_project, target_tier, str(old_name), host_ip, server_color, colorstack_map.get(key_name)))
                            FileUtil.appendtoFile('%s\configModifier_update_host_service.log' % (settings.LOG_ROOT_PATH), 'Updated server ip %s %s %s from %s to %s' %(target_env, target_project, target_tier, str(old_name), host_ip))
                            found = True
                            break;
                        if not found and models.ServerTypes.objects.filter(project__name=target_project, server_tier__name=target_tier).exists() and models.Environments.objects.filter(environment=target_env).exists():
                            server_type_obj= models.ServerTypes.objects.filter(project__name=target_project, server_tier__name=target_tier).first()
                            env_obj= models.Environments.objects.filter(environment=target_env).first()
                            models.Servers.objects.create(server_name=host_ip, environment_id=env_obj,server_type=server_type_obj,enabled=True,warnings=0)
                            FileUtil.appendtoFile('%s\configModifier_update_host.log' % (settings.LOG_ROOT_PATH), 'Created server %s %s %s %s server color: %s env color: %s' %(target_env, target_project, target_tier, host_ip, server_color, colorstack_map.get(key_name)))
                            FileUtil.appendtoFile('%s\configModifier_update_host_service.log' % (settings.LOG_ROOT_PATH), 'Created server %s %s %s %s' %(target_env, target_project, target_tier, host_ip))
        except:                
            FileUtil.appendtoFile('%s\configModifier_update_host.log' % (settings.LOG_ROOT_PATH), 'Exception happened when updating host: %s %s %s\n%s' %(env, project, tier, traceback.format_exc())) 
            FileUtil.appendtoFile('%s\configModifier_update_host_service.log' % (settings.LOG_ROOT_PATH), 'Exception happened when updating host: %s %s %s\n%s' %(env, project, tier, traceback.format_exc())) 
 
def getEnvColorStack(env, project): 
        if project == 'BOS':
            color_stack = views_api.EnvironmentsColorStack.get_env_color(AWS_CM_ENV_MAP.get(env))
            return  color_stack if color_stack in [GREEN_STACK, BLUE_STACK ] else ""
        
        custom_filter = [
                    {
                        'Name': 'tag:Environment',
                        'Values': [env]
                    },
                    {
                        'Name': 'tag:Project',
                        'Values': [project]
                    },
                    {
                        'Name': 'tag:Tier',
                        'Values': ["APP"]
                    },
                ]
        session = boto3.Session(profile_name=env.lower())  
        client = session.client(service_name,region_name=region_name)      
        instances = client.describe_instances(Filters=custom_filter)['Reservations']
        for server in instances:
            return getColorStack(server);
def getColorStack(server):
    Colorstack = ''
    Name = ''
    for tag in server['Instances'][0]['Tags']:
        if tag['Key'] == 'Colorstack':
            Colorstack = tag['Value']
        if tag['Key'] == 'Name':
            Name = tag['Value']
    
    if Colorstack == BLUE_STACK and Name.endswith('-b'):
        return BLUE_STACK
    elif Colorstack == GREEN_STACK and Name.endswith('-g'):
        return GREEN_STACK
    else:
        return ''

@shared_task
def check_lock():
#     QA-10410
    lock_id = 186676
    lock_obj =  models.CurrentLocks.objects.get(id=lock_id)
    result,current,expect = views.checkLockValueChangedAsRequest(lock_id)
    if current == 'N/A':
        FileUtil.appendtoFile('%s\configModifier_check_lock.log' % (settings.LOG_ROOT_PATH), 'Skip as network of lock %s is not accessible.' %(str(lock_id)))
        return
#     FileUtil.appendtoFile('%s\configModifier_check_lock.log' % (settings.LOG_ROOT_PATH), 'result: %s, current is %s, expect is %s' %(str(result), current, expect))
    if not result:
        lock_obj.is_active=False
        lock_obj.duration=144000
        lock_obj.save()
    else:
        return
    i=1
    is_active = False
    while i< 360:
        if models.CurrentLocks.objects.get(id=lock_id).is_active==True:
            FileUtil.appendtoFile('%s\configModifier_check_lock.log' % (settings.LOG_ROOT_PATH), 'Lock is active.')
            is_active = True
            break
        time.sleep(10)
        i += 1
    if is_active:
        data = '''<build buildTypeId="Gbos_Utilities_AwsRestartService_RestartServiceRh">
                <properties>
                <property name="system.action" value="RestartService">
                <type rawValue="System Parameters" />
                </property>
                <property name="system.qa_env" value="pie">
                <type rawValue="System properties" />
                </property>
                <property name="system.tier" value="rh">
                <type rawValue="System properties"/>
                </property>
                <property name="service_name" value="GDRequestHandler">
                <type rawValue="System properties"/>
                </property>
                
                <property name="service_action" value="RestartService">
                <type rawValue="System Parameters" />
                </property>
                
                <property name="system.server" value="01">
                <type rawValue="System properties" />
                </property>
                <property name="service_name" value="GDRequestHandler">
                <type rawValue="System properties"/>
                </property>
                </properties>
                </build>'''
        headers = {'Content-type':'application/xml', 'Authorization':'Basic cWFfdGVzdF9hdXRvbWF0aW9uOkdyMzNuRG90IQ=='}
        response = requests.post("https://teamcity/httpAuth/app/rest/buildQueue",verify=False,data=data,headers=headers)
        FileUtil.appendtoFile('%s\configModifier_check_lock.log' % (settings.LOG_ROOT_PATH), 'Service restarting...' + ( ', status code: ' + str(response.status_code) if response else '' ))