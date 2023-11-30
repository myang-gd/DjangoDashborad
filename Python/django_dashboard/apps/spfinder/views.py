from django.shortcuts import render
from apps.spfinder.sourcesearch import APIClient
from apps.spfinder.util.mssql import Mssql
import logging
from multiprocessing.dummy import Pool as ThreadPool
import threading
import itertools
import concurrent.futures
from django.core.cache import cache
import json
from django.http.response import HttpResponse
def spfinder(request):
    logger = logging.getLogger("spfinder")
    context_dict={}
    logger.info("Calling spFinder View")
    database_server_dict = {}
    for database_server_item in getAllDatabaseServers():
        database_server_dict[database_server_item] = database_server_item
    context_dict['database_server_dict'] = database_server_dict
    logger.info("All Database Servers Fetched")
    lock = threading.Lock()   
    if request.method == 'POST':
        context_dict['result'] = 'true'
        databaseServersList = request.POST.getlist('databaseServers')
        x_progress_id = request.POST.get('X-Progress-ID')
        # Get All DB Servers and run SP to find all SP procedure in parallel on DB servers
        dbServerListPool = ThreadPool(len(databaseServersList))
        dbServerListPoolResult = dbServerListPool.map(findAllSp, databaseServersList)
        dbServerListPool.close()
        # Wait to get all result set from SPs 
        dbServerListPool.join()
        spResultSet = list(itertools.chain(*dbServerListPoolResult))
        for spItem in spResultSet:
            for k, v in sorted(spItem.items()):
                spItem[k] = str(v)
        count = 0
        progress = 0
        cache.set(x_progress_id, progress) 
        total_count = len(spResultSet)
        apiClient = APIClient()
        spNameList = []
        # Create array of all SP names returned from each DB Server
        for spItem in spResultSet:
            spNameList.append(spItem.get('SP_Name'))
        resultDic = {} # {spName : [file Path location 1, file path location 2, etc..] }
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            future_to_sp_name = {executor.submit(invokeSourceSearchAPI, apiClient, spName, resultDic): spName for spName in spNameList}
            for future in concurrent.futures.as_completed(future_to_sp_name):
                sp_name = future_to_sp_name[future]
                lock.acquire()
                count += 1
                print("Finished count: " + str(count))
                progress = int(count/total_count*100.0)
                cache.set(x_progress_id, progress)
                lock.release()
                print('Finished process sp: %s' % (sp_name))
        
        for spItem in spResultSet:
            spItem['References'] = resultDic.get(spItem.get('SP_Name'))         
                
        context_dict['spList'] = spResultSet        
        cache.delete(x_progress_id)
    return render(request, 'spfinder.html', context_dict)
def getProgress(request):
    context_dict = {}
    x_progress_id = request.GET['X-Progress-ID']
    if x_progress_id:
        progress = cache.get(x_progress_id)
        if progress is None:
            progress = 100
    else:
        progress = 0
    
    context_dict['progress'] = progress
    json_posts = json.dumps(context_dict)
    return HttpResponse(json_posts, content_type='application/json')

def findAllSp(databaseServer):
    mssql = Mssql(server=databaseServer, db='master', user='qa_automation', pwd='Gr33nDot!')
    return mssql.ExecSPFinderSPFlow()

def invokeSourceSearchAPI(apiClient, spNameParameter, resultDic):
    print ("Starting thread: " + threading.current_thread().getName())
    ref_list = apiClient.send_get_all_pages(spNameParameter, 'q=' + spNameParameter + '&path=DotNet%2Fintegration%2F+&project=DotNet')
    resultDic[spNameParameter] = ref_list
    print ("Finished thread: " + threading.current_thread().getName())
def getAllDatabaseServers():
    databaseServerList = ["GDCQA4IPSNRT01", "GDCQA4IPSSQL01", "GDCQA4IPSSSIS01", "GDCQA4-NRT01", "GDCQA4-REP03", "GDCQA4-SQL01", "GDCQA4SSIS201", "GDCQA4V3SQL21"]
    return databaseServerList;

