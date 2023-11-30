import time
from multiprocessing import Process, Queue
from apps.healthcheck.logger import Logger
from .api_runner import getServiceResult
class APIRunnerThread(Process):
    def __init__(self, operation_map=None, service_map=None, endpoint:[str]=None, vip_name=None):
        super().__init__()
        self._operation_map = operation_map
        self._service_map = service_map
        self._endpoint = endpoint
        self._vip_name = vip_name
        self._return = {}
        self.queue = Queue()
        self.result = {}
        Logger.enable()
    def run(self):
        Logger.log('Starting finder run')
        try:
            self._return =  getServiceResult(self._operation_map, self._service_map, self._endpoint, self._vip_name)
        except Exception as e:
            Logger.log('Failed to find unused cases due to ' + str(e))
        
        self.queue.put(self._return)
        time.sleep(10)     
        Logger.log('Process done!!!!!')
    def getResult(self):        
        try:    
            self.result = self.queue.get_nowait()
        except:
            pass
        return self.result



    