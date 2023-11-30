import django
django.setup()
from apps.ConfigModifier import models,views,tasks
import requests
import json
lock_id = 186676
lock_obj =  models.CurrentLocks.objects.get(id=lock_id)
tasks.processUpdateHost({})
tasks.check_lock()

result,current,expect = views.checkLockValueChangedAsRequest(lock_id)

if result:
    lock_obj.is_active=True
    lock_obj.duration=144000
    lock_obj.save()
else:
    print("kkk")
# for t1 in t:

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



#     print(t1)

# data = {
#       "value": "true",
#       "duration": 2,  
#       "user_name": "mzhao",
#       "environment_name": "AWS-PI",
#       "include_all_servers": True,
#       "server_type": "BOS_RH",
#       "file": "gdc\\Services\\RequestHandler\\RequestHandler.dll.config",
#       "config": "add key=IsBypassX9Limitation value="
# }
# data_json = json.dumps(data)
# headers = {'Content-type': 'application/json'}
# response = requests.post("https://gdqatools:8200/configModifier/locks/",verify=False,data=data_json,headers=headers)
# 
# print(response)

# import boto3
# from boto3.dynamodb.conditions import Key
# region_name='us-west-2'
# service_name = 'dynamodb'
# env = "dynamodb"
# session = boto3.Session(profile_name=env.lower())  
# client = session.client(service_name,region_name=region_name)
# existing_tables = client.list_tables()['TableNames']
# tables = client.describe_endpoints()
# tables = client.describe_table(TableName='End')
# response = client.query(
#     TableName='Detail',
#     KeyConditionExpression='CallSID = :sid AND InsertTime = :insert_time',
#     ExpressionAttributeValues={
#         ':sid': {'S': 'CA597c542cf83c93b343b90cd7429925b6'},
#         ':insert_time': {'N': '1624000562838'}
#     }
# )
# 
# 
# dynamodb = session.resource('dynamodb', region_name=region_name)
# table = dynamodb.Table('Header')
# response = table.query(
#     KeyConditionExpression=Key('CallSID').eq("CA2020b0186528c3d7b9b437551a07adc6")
# )
# 
# response['Items']
