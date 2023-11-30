from P4 import P4,P4Exception
from common_utils.xml_util import XmlUtil
from .logger import Logger
class Perforce:
    
    USER_NAME = "qa_test_automation";
    ENCRYPTED_PASSWORD = "U2GjyDG7WibISyIK0h/7AQ=="
    DECRYPT_URL = 'http://gdcqatools01:8081/EncryptionService/rest/encryption/decrypt?token='
    SERVER_URL = 'https://pd'
    jira = None 
    
    def __init__(self):
        self.p4 = P4()
        self.p4.port = "GDCHELIX01:5050"
        self.p4.user = "qa_test_automation"
        self.p4.password = 'Gr33nDot!'
        self.p4.connect()
        self.p4.run_login()
    def read_file(self, depot_file, encoding = "utf8", size_limit = 2*1024*1024) -> bytes:
        """ read the file content as byte array
        """
        self.keep_alive()
        result = bytes('', encoding = encoding)
        if self.p4:
            try:
                size = self.getFileSize(depot_file)
                if size is not None and size > size_limit:
                    Logger.log('Skipped to read file %s due to size %s exceeds size limit %s or failed to get size' %(str(depot_file),str(size),str(size_limit)))
                    return result
                out_put_list = self.p4.run_print(depot_file) 
            except P4Exception as e:
                if 'no such file' not in str(e):
                    Logger.log('Failed to read file %s due to %s' %(str(depot_file), str(e)))
            else:
                if len(out_put_list) >= 2:
                    result =  bytes(out_put_list[1], encoding = encoding)
            finally:
                return result
        else:
            return result
    def getFileSize(self, depot_file):
        try:
            return int(self.p4.run('sizes', depot_file)[0]['fileSize'])
        except Exception as e:
            if 'no such file' not in str(e):
                Logger.log('Failed to get size of file %s due to %s' %(str(depot_file), str(e)))      
            return -1
    
    def get_subdirs(self, depot_path:str, isFile = False, isFileRecursive = False) -> []:
        """ get subdirectories for a given depot path, return as list
            if isFile set as True then list files as return
        """
        self.keep_alive()
        dirs = []
        if not depot_path:
            return dirs   
        re = []
        if isFile and isFileRecursive:
            if str(depot_path).endswith('/'):
                depot_path +=  '...'
            else:
                depot_path +=  '/...'
        else:
            if str(depot_path).endswith('/'):
                depot_path +=  '*'
            else:
                depot_path +=  '/*'      
                    
        if self.p4:
            try:
                if isFile:
                    dirs = self.p4.run("files", str(depot_path))
                else:
                    dirs = self.p4.run("dirs", str(depot_path))
            except P4Exception as e:
                Logger.log('Failed to get subdirectories or files for path %s due to %s' %(str(depot_path), str(e)))
            finally:
                return dirs
        else:
            return dirs   
    def find_project_dirs(self, root_path):  
        settingFile = self.read_file(root_path + '/settings.xml')
        projectName = ''
        if settingFile:
            projectName = XmlUtil.get_str_element(settingFile, '//con:soapui-project/@name',  {'con':'http://eviware.com/soapui/config'})
        if projectName:
            return [root_path]
         
        project_dirs = self.get_subdirs(root_path)
        return_list = []
        for project_dir in project_dirs :
            return_list.extend(self.find_project_dirs(project_dir['dir']))
             
        return return_list
    def find_project_dirs_none_recur(self, root_path):           
        files = self.get_subdirs(root_path, True, True)
        project_file_paths = [file['depotFile'] for file in files if file['action'] != 'delete' and file['action'] != 'move/delete' 
                              and file['depotFile'].endswith('settings.xml')]
        last_count_index = 0
        last_path = ''
        return_list = []
        for file_path in project_file_paths:
            current_count = file_path.count("/")
            current_path = file_path[0:file_path.rfind('/')]
            if last_count_index != 0 and current_count < last_count_index and last_path != current_path and current_path in last_path and file_path.endswith('/settings.xml'):
                return_list.append(file_path[:-13])
            last_count_index = current_count
            last_path = current_path
             
        return return_list
#     def find_project_dirs(self, root_path):  
#         settingFile = self.read_file(root_path + '/settings.xml')
#         projectName = ''
#         if settingFile:
#             projectName = XmlUtil.get_str_element(settingFile, '//con:soapui-project/@name',  {'con':'http://eviware.com/soapui/config'})
#         if projectName:
#             return [root_path]
#         
#         project_dirs = self.get_subdirs(root_path)
#         return_list = []
#         current_path = ""
#         for project_dir in project_dirs :
#             current_path = project_dir
#             current_SettingFile = self.read_file(current_path + '/settings.xml')
#             if current_SettingFile:
#                 return_list.extend(current_path)
#                 continue;
#             else:
#                 
#             return_list.extend(self.find_project_dirs(project_dir['dir']))
#             
        return return_list
    def release(self):
        if self.p4 :
            self.p4.disconnect()
    def keep_alive(self):
        if not self.p4.connected():
            self.p4.port = "GDCHELIX01:5050"
            self.p4.user = "qa_test_automation"
            self.p4.password = 'Gr33nDot!'
            self.p4.connect()
        

