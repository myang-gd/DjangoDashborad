import urllib.request as re
import xml.etree.ElementTree as et
import json
from bs4 import BeautifulSoup

# Confluence API settings
testRailAPI_Base_URL = 'https://wiki.nextestate.com/rest/api/content'
Project_Release_Schedule_Page_Title_Map =  {'GBOS' : 'GBOS%20/%20GSS%20/%20BUX%20Release%20Schedule',
                                'MOVE' : 'MOVE+Release+Schedule',
                                'Tax' : 'TAX+2.0+Release+Schedule',
                                'CRM' : 'Legacy+Release+Schedule'
}
headers = {'Authorization' : 'Basic cWFfdGVzdF9hdXRvbWF0aW9uOkdyMzNuRG90IQ=='}

# get confluence content
def getContentsFromConf():
    res_map = {}
    for project_Name, page_Title in Project_Release_Schedule_Page_Title_Map.items():
        res_dict=[]
        testRailAPI_URL = testRailAPI_Base_URL + '?title=' + page_Title + '&expand=body.storage'        
        req = re.Request(url=testRailAPI_URL, headers=headers)
        res = re.urlopen(req)
        res_str = str(res.read().decode('utf-8'))
        json_obj = json.loads(res_str)
        json_dict = json_obj['results'][-1]['body']['storage']['value']
        value_soup = BeautifulSoup(str(json_dict))
        table_value = value_soup.findAll('table')[0]
        table_value = ''.join(str(table_value).split('<thead>')).strip()
        table_value = ''.join(str(table_value).split('</thead>')).strip()
        table_value = ''.join(str(table_value).split('<tbody>')).strip()
        table_value = ''.join(str(table_value).split('</tbody>')).strip()
        table = et.fromstring(table_value)
        rows = iter(table)
        next(rows)
        table_headers = [''.join(col.itertext()).strip() if col.text is None else str(col.text).strip() for col in next(rows)]        
        for row in rows:
            values = [''.join(col.itertext()).strip() if col.text is None else str(col.text).strip() for col in row]
            res_dict.append(dict(zip(table_headers, values)))
        res_map[project_Name]=res_dict
    return res_map