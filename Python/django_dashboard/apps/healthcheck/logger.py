from common_utils.io_util import FileUtil
import os
class Logger():
        LOG_ROOT_PATH = '%s\django_dashboard_log' %(os.environ['SYSTEMDRIVE'])
        _fileName = '%s\healthcheck_main.log' % (LOG_ROOT_PATH)
        FileUtil.createFile(_fileName)
        _enable = False
        
        @classmethod 
        def log(cls, messsage:str):
            if cls._enable:
                FileUtil.appendtoFile(cls._fileName, messsage)
                print(messsage)
        @classmethod
        def enable(cls):
            cls._enable = True
        @classmethod
        def disable(cls):
            cls._enable = False