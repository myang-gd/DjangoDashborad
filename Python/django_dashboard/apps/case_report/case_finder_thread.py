import time
from common_utils.peforce import Perforce
from multiprocessing import Process, Queue
from apps.case_report.case_finder import find_unused_cases_multithread
from .case_finder import clearProgress
from apps.case_report.logger import Logger

class FinderThread(Process):
    def __init__(self, project_id=None, root_path_list:[str]=None, progress_id=None, suite_ids:[str]=None, all_cases=False):
        super().__init__()
        try:
            self._p4 = Perforce()
        except Exception as e:
            Logger.log('Failed to start perforce client due to ' + str(e))
            return
        self._project_id = project_id
        self._root_path_list = root_path_list
        self._progress_id = progress_id
        self._return = []
        self.queue = Queue()
        self.suite_ids = suite_ids
        self.all_cases = all_cases
    def terminate(self):
        '''
        Terminate process; sends SIGTERM signal or uses TerminateProcess()
        '''
        self.release()
        super(FinderThread, self).terminate()

    def run(self):
        Logger.log('Starting finder run')
        try:
            self._return = find_unused_cases_multithread(self._project_id, self._root_path_list, self._p4, self._progress_id, self.suite_ids, self.all_cases)
        except Exception as e:
            Logger.log('Failed to find unused cases due to ' + str(e))
        
        self.queue.put({'result': self._return})
        
        Logger.log('Sleeping 10 seconds to wait main thread retrieving the result')        
        time.sleep(10)                
        Logger.log('Process done!!!!!')
    def getResult(self):
        return self.queue.get()
        
    def release(self):
        if self._p4:
            Logger.log('releasing resource')  
            try:
                self._p4.release()
                clearProgress(self._progress_id)
            except:
                pass
            Logger.log('Finished releasing resource')  




    