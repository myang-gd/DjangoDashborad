'''
Created on Jun 21, 2016

@author: zbasmajian
'''

import urllib.request, urllib.error
import requests
from lxml import html
class APIClient:
    def __init__(self):
        self.__base_url = 'http://sourcesearch/source/search?'
        self.__root_url = 'http://sourcesearch'
    
    def send_get(self, uri):
        return self.__send_request('GET', uri, None)
    
    def send_get_all_pages(self, spNameParameter, uri, n=1000, start=0):
        reponse_bytes = self.__send_request_response_byte('GET', ('%s&n=%s&start=%s' % (uri, n, start)), None)       
        refs = self.__get_refs(spNameParameter, reponse_bytes)
        refs_all = refs
        while(refs):
            start += n 
            reponse_bytes = self.__send_request_response_byte('GET', ('%s&n=%s&start=%s' % (uri, n, start)), None)       
            refs = self.__get_refs(spNameParameter, reponse_bytes)
            refs_all.extend(refs)
        
        return refs_all
                 
    def __get_refs(self, spNameParameter, reponse_bytes):
        if not reponse_bytes:
            return []
        tree = html.fromstring(reponse_bytes.content)
        file_refs = tree.xpath('//table/tr/td[@class="f"]/a/@href') 
        result = []
        for ref in file_refs:
            if ref.endswith(spNameParameter + '.sql') == False: 
                result.append(self.__root_url + ref)
        
        return result

    def __send_request_response_byte(self, method, uri, data):
        
        url = self.__base_url + uri             
        e = None        
        try:
            response = requests.get(url)
        except urllib.error.HTTPError as ex:
            response = ex.read().decode('utf-8')
            e = ex      
            
        if e != None:
            raise APIError('Source Search API returned Http %s (%s)' % (e.code, response))
        
        return response
    
    def __send_request(self, method, uri, data):
    
        url = self.__base_url + uri
        
        request = urllib.request.Request(url)
        
        e = None
        
        try:
            response = urllib.request.urlopen(request).read().decode('utf-8')
        except urllib.error.HTTPError as ex:
            response = ex.read().decode('utf-8')
            e = ex
            
        if response:
            result = response
        else:
            result = {}
            
        if e != None:
            raise APIError('Source Search API returned Http %s (%s)' % (e.code, response))
        
        return result

class APIError(Exception):
    pass       