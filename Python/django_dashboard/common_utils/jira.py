from jira import JIRA
from  requests import packages
import threading
import requests
class Jira:
    
    __singleton_lock = threading.Lock()
    __singleton_instance = None
    USER_NAME = "qa_test_automation";
    ENCRYPTED_PASSWORD = "U2GjyDG7WibISyIK0h/7AQ=="
    DECRYPT_URL = 'http://gdcqatools01:8081/EncryptionService/rest/encryption/decrypt?token='
    SERVER_URL = 'https://pd'
    jira = None 
    def __init__(self):
        packages.urllib3.disable_warnings()
        options = {
                   'server': self.SERVER_URL,
                   'verify': False,
                   }
        response = requests.get(self.DECRYPT_URL + self.ENCRYPTED_PASSWORD)
        if response.status_code != 200:
            response.raise_for_status()
        else:
            decrypted_password = response.json().get('Token')
        self.jira = JIRA(options, basic_auth= (self.USER_NAME, decrypted_password))

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance
    
    
    def isApproved(self, jiraNumber):
        if jiraNumber:
            try:
                issue = self.jira.issue(jiraNumber)
                for field_name in issue.raw['fields']:
                    if 'conditional rule' in str(issue.raw['fields'][field_name]) and 'Approval Req' in str(issue.raw['fields'][field_name]):
                        return False
            except:
                return False
            else:
                return True
        else:
            return False
    def isValid(self, jiraNumber):
        if jiraNumber:
            try:
                issue = self.jira.issue(jiraNumber)
            except:
                return False
            else:
                if issue:
                    return True
                else:
                    return False
        else:
            return False
    def getProject(self, projectName):
        if projectName:
            try:
                for project in self.jira.projects():
                    if project.name == projectName:
                        return JiraProject(project.name, project.key, project.id)
            except:
                return None
            else:
                return None
        else:
            return None
    def getProjectKey(self, projectName):
        project = self.getProject(projectName)
        if project:
            return project.key
        else:
            return None
    def getIssue(self, jiraNumber):
        try:
            issue = self.jira.issue(jiraNumber)
        except:
            return None
        else:
            if issue:
                return JiraIssue( issue.raw['fields']['summary'], issue.raw['fields']['status']['name'], 
                                  issue.id, issue.raw['fields']['created'])
            else:
                return None
class JiraProject:
    name = ''
    key = ''
    pid = ''
    def __init__(self, name, key, id):
        self.name = name
        self.key = key
        self.id = id  
class JiraIssue:
    summary = ''
    status = ''
    id = ''
    createdDate=''
    def __init__(self, summary, status, id, createdDate):
        self.summary = summary
        self.status = status
        self.id = id 
        self.createdDate = createdDate 