from django.shortcuts import render
from django.http import HttpResponse

import json
from jira import JIRA

#JIRA Tool settings
jiraURL = 'https://pd.nextestate.com'
sslVerify = False
basic_auth=("qa_test_automation", "Gr33nDot!")
options = {'server':jiraURL,'verify': sslVerify}

JIRA_Project_Borard_Mapping =  {'GBOS': {
                                            'name':'Green Dot Banking OS',
                                            'board_id': 467
                                        }
                                }

def JiraTool(request):
    return render(request, 'jiraTool.html',{'project_list':JIRA_Project_Borard_Mapping})   



def loadSprints(request):
    jiraclient = JIRA(options, basic_auth=("qa_test_automation", "Gr33nDot!"))

    sprints_arr = []
    boardID = request.POST.get("board_id")  
                  
    sprints = jiraclient.sprints(boardID,False)
    for sprint in sprints:
        sprint_dict = {}
        sprintDetail = json.loads(json.dumps(sprint.raw))
 
        sprint_dict['id'] = sprintDetail['id']
        sprint_dict['name'] = sprintDetail['name']
        sprint_dict['state'] = sprintDetail['state']
            
        if(sprint not in sprints_arr and sprintDetail['state'] != 'FUTURE' and "gbos" in str(sprint_dict['name']).lower()):
            sprints_arr.append(sprint_dict)
    
    if(len(sprints_arr)>=10):
        sprints_arr = sprints_arr[-10:]
    sprints_arr.reverse()
    return HttpResponse(json.dumps({'sprint_list': sprints_arr}), content_type='application/json')
  
          
def SearchJira(request):
    jiraclient = JIRA(options, basic_auth=("qa_test_automation", "Gr33nDot!"))
    request.session.clear()
        
    storyPoint_map = {}

    sprint = request.POST.get('sprint') 
    qaEngineers = request.POST.get('QAs').strip() 
    print(sprint)
    print(qaEngineers)
    qaStr = ''
    qaStrFinal = ''
    if(qaEngineers!=None and qaEngineers!=''):
        qaArr = qaEngineers.split(',')
        for qa in qaArr:
            qaStr = qaStr + '"' + qa.strip() + '",'
        qaStrFinal = 'And "QA Engineer" in (' + qaStr[0:-1] + ')'
    else:
        qaStrFinal = 'And "QA Engineer" is not EMPTY'
    searchString = ' Sprint = \'' + sprint + '\' '+ qaStrFinal
    print(searchString)
    
    jiraTickets = jiraclient.search_issues(searchString, startAt=0, maxResults=-1, validate_query=True, fields=None, expand=None, json_result=None )
    print('ticket number = ' + str(len(jiraTickets)))
    for ticket in jiraTickets:
        ticketDetail_map = {}
#        ticketDetail_json = json.loads(json.dumps(ticket.raw))
        ticketDetail_json = ticket.raw
        if 'customfield_13213' not in ticketDetail_json['fields'].keys():
            break
        if 'customfield_10002' not in ticketDetail_json['fields'].keys():
            break
        qa = ticketDetail_json['fields']['customfield_13213']['displayName']
        ticketDetail_map['qa'] = qa
        ticketDetail_map['point'] = ticketDetail_json['fields']['customfield_10002']
        ticketDetail_map['url'] = jiraURL + '/browse/' + ticketDetail_json['key']
        ticketDetail_map['status'] = ticketDetail_json['fields']['status']['name']
        ticketDetail_map['type'] = ticketDetail_json['fields']['issuetype']['name']

#         if ticketDetail_map['url'] == 'https://pd/browse/GBOS-21490':
#             print(str(ticketDetail_json))
#         print('===============')
#         print('before = '+ str(storyPoint_map))

        if qa not in storyPoint_map:
            storyDetail_arr = []
            storyDetail_arr.append(ticketDetail_map)
            storyPoint_map[qa] = storyDetail_arr
        else:
            storyPoint_map[qa].append(ticketDetail_map)
    
    request.session['storyPoint_map'] = storyPoint_map     
    #print(storyPoint_map)
    return HttpResponse(json.dumps({'storyPoint_map': storyPoint_map}), content_type='application/json')

def assignDetail(request):

    if request.method == 'GET' and 'QA' in request.GET:            
        name = request.GET.get('QA')
    return render(request, 'assignDetail.html',{'assignDetail':json.dumps(request.session.get('storyPoint_map')[name])})   

                      