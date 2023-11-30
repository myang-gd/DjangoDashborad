from django.test import TestCase

# Create your tests here.
from jira import JIRA
from jira.client import GreenHopper
import requests 

import json



options = {'server':'https://pd','verify': False}
basic_auth=("qa_test_automation", "Gr33nDot!")
sslVerify = False
geenkeeper = 'https://pd/rest/greenhopper/latest/rapidviews/list?projectKey=' + 'GBOS'
jira1 = JIRA(options, basic_auth=("qa_test_automation", "Gr33nDot!"))

# sprints = jira1.sprints(467,False)

 
jiraTickets = jira1.search_issues('project=GBOS And Type = Story And Sprint = \'GBOS Milestone 47 - 10/22/2019\'', startAt=0, maxResults=-1, validate_query=True, fields=None, expand=None, json_result=None )
 
for ticket in jiraTickets:
    ticketDetail_json = json.loads(json.dumps(ticket.raw))
    print(ticketDetail_json['fields']['assignee'])
    print(ticketDetail_json['fields']['customfield_10002'])
    print('')
resp = requests.get(geenkeeper, auth= basic_auth, verify=sslVerify)
boards = resp.json()['views']
boards.reverse()
sprints_arr = []
for board in boards:
    sprints = jira1.sprints(board['id'],False)
    for sprint in sprints:
        sprint_dict = {}
        sprintDetail = json.loads(json.dumps(sprint.raw))

        sprint_dict['id'] = sprintDetail['id']
        sprint_dict['name'] = sprintDetail['name']
        if(sprint_dict not in sprints_arr):
            sprints_arr.append(sprint_dict)
    break  
print(sprints_arr)
 
jira1 = JIRA(options, basic_auth=("qa_test_automation", "Gr33nDot!"))



projects = jira1.projects() 
projectsArr = []
boards = jira1.boards()
for board in boards:
    print(board.raw)
    break    
    
sprints = jira1.sprints(467,False)
for sprint in sprints:
    print(sprint.raw)
    break

project = jira1.project("GBOS") 

print(project.raw)


tickets = jira1.search_issues('project=GBOS And Type = Story And Sprint = \'GBOS Milestone 48 - 11/5/2019\' And assignee in (\'William Chen\')')


    
storyPointMap = {}
for ticket in tickets:
    ticketDetail = json.loads(json.dumps(ticket.raw))
    if ticketDetail['fields']['assignee']!= None:
        assignee = ticketDetail['fields']['assignee']['displayName']
        point = ticketDetail['fields']['customfield_10002']
    
    
        if assignee not in storyPointMap:
            storyPointMap[assignee] = point
        else:
            storyPointMap[assignee] = storyPointMap[assignee] + point

print(storyPointMap)


#print(json.dumps(issue.raw)['fields']['summary'])
#/print("issue.fields.summary = " + issue.fields.summary)  
#print("issue.fields.customfield_10002=" + str(issue.fields.customfield_10002))
#print("issue.fields.assignee="+ str(issue.fields.assignee) )        
       
