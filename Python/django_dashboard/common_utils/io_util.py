from django.core.files import File
from django.utils import timezone
import traceback, sys
import logging
import os
class FileUtil:
    
    @classmethod
    def createFile(cls, fileName):
        logger = logging.getLogger("FileUtil")
        try:
            if not os.path.exists(os.path.dirname(fileName)):
                os.makedirs(os.path.dirname(fileName))
            if not os.path.exists(fileName):
                open(fileName, 'w').close() 
            return True
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            logger.error("Failed to create file %s due to %s\nStacktrace: %s" %(fileName, str(e), str(traceback.format_tb(traceback_))))
            return False
    
    @classmethod
    def appendtoFile(cls, fileName, content, newline = True, withTimeStamp = True):
        logger = logging.getLogger("FileUtil")
        myfile = None
        f = None
        if not cls.createFile(fileName):
            return
        try:
            with open(fileName, "a") as f:
                myfile = File(f)
                if withTimeStamp:
                    content = '[%s] ' % str(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))  +  content
                if newline and myfile.size != 0:
                    myfile.write('\n' + content) 
                else:              
                    myfile.write(content)
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            logger.error("Failed to write log to file %s due to %s\nStacktrace: %s" %(fileName, str(e), str(traceback.format_tb(traceback_))))
        finally:
            if myfile:
                myfile.closed
            if f:
                f.closed
    