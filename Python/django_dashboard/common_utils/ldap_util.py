from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE
import re 

class LdapUtil:
    
    @classmethod
    def getGroupUserNames(cls, group_name):
        userNameList = []
        try:
            conn = Connection(Server('nextestate.com', port=389, use_ssl=False),
              auto_bind=AUTO_BIND_NO_TLS, user='nextestate\\qa_test_automation',
              password='Gr33nDot!')
         
            search_filter = ('(&(objectClass=person)(memberOf=CN=%s,OU=Distribution,OU=Groups,DC=nextestate,DC=com))' %(group_name))
            conn.search(search_base='OU=Information Technology,DC=nextestate,DC=com', 
                search_filter=search_filter, search_scope=SUBTREE, 
                attributes = ['sAMAccountName','memberOf'], size_limit=0) 
            for entry in conn.entries:
                user_name = entry.sAMAccountName.value
                if user_name and user_name not in userNameList:
                    userNameList.append(user_name)           
        except Exception as e:
            raise Exception("Exception was caught when getGroupUserNames exception: " + str(e))
        else:
            return userNameList
    
    @classmethod
    def getUserGroupNames(cls, user_name):
        groupNameList = []
        try:
            conn = Connection(Server('nextestate.com', port=389, use_ssl=False),
            auto_bind=AUTO_BIND_NO_TLS, user='nextestate\\qa_test_automation',
            password='Gr33nDot!')
         
            search_filter = ('(&(objectClass=person)(sAMAccountName=%s))' %(user_name))
            conn.search(search_base='DC=nextestate,DC=com', 
                search_filter=search_filter, search_scope=SUBTREE, 
                attributes = ['sAMAccountName','memberOf'], size_limit=0) 
            for entry in conn.entries:
                if 'memberOf' not in entry:
                    return groupNameList
                memberList = entry.memberOf.value
                for member in memberList: #e.g. 'CN=ADFS-O365-Mail,OU=Security,OU=Groups,DC=nextestate,DC=com'
                    pattern = re.compile(r'^CN=(?P<group>[^\,]+),OU=.*$') 
                    match = pattern.match(member) 
                    if match:
                        groupNameList.append(match.group('group'))    
        except Exception as e:
            raise Exception("Exception was caught when getUserGroupNames exception: " + str(e))
        else:
            return groupNameList
    @classmethod
    def getUserExpires(cls, user_name):
        accountExpires = 'N/A'
        try:
            conn = Connection(Server('nextestate.com', port=389, use_ssl=False),
            auto_bind=AUTO_BIND_NO_TLS, user='nextestate\\qa_test_automation',
            password='Gr33nDot!')
         
            search_filter = ('(&(objectClass=person)(sAMAccountName=%s))' %(user_name))
            conn.search(search_base='DC=nextestate,DC=com', 
                search_filter=search_filter, search_scope=SUBTREE, 
                attributes = ['accountExpires'], size_limit=0) 
            for entry in conn.entries:
                accountExpires = entry.accountExpires.value
        except Exception as e:
            raise Exception("Exception was caught when getUserExpires exception: " + str(e))
        else:
            return accountExpires
    @classmethod
    def getUserAccountControl(cls, user_name):
        userAccountControl = 'N/A'
        try:
            conn = Connection(Server('nextestate.com', port=389, use_ssl=False),
            auto_bind=AUTO_BIND_NO_TLS, user='nextestate\\qa_test_automation',
            password='Gr33nDot!')
         
            search_filter = ('(&(objectClass=person)(sAMAccountName=%s))' %(user_name))
            conn.search(search_base='DC=nextestate,DC=com', 
                search_filter=search_filter, search_scope=SUBTREE, 
                attributes = ['userAccountControl'], size_limit=0) 
            for entry in conn.entries:
                if 'userAccountControl' not in entry:
                    return userAccountControl
                else:
                    userAccountControl = entry.userAccountControl.value
        except Exception as e:
            raise Exception("Exception was caught when getUserExpires exception: " + str(e))
        else:
            return userAccountControl