import urllib.request as urlequest
import xml.etree.ElementTree as et
import json
import re
from bs4 import BeautifulSoup 
from apps.CommonAPI.ConfAPI.utils import ProductDB
import requests
from requests_ntlm import HttpNtlmAuth
from common_utils.constant import Constant
import concurrent.futures
from collections import OrderedDict

Conf_Base_URL = 'https://wiki.nextestate.com/rest/api/content'
Project_Feature_Page_Title_Map =  {'care' : 'CRM+BaaS+Service+-+New+Partner+on+Board',
                                   'care_ui' : 'CRM+BaaS+UI+-+New+Partner+on+Board',
                                   'ivr': 'IVR+BaaS+-+New+Partner+on+Board'
}
headers = {'Authorization' : 'Basic cWFfdGVzdF9hdXRvbWF0aW9uOkdyMzNuRG90IQ=='}
headers_put = {'Content-type':'application/json', 'Authorization' : 'Basic cWFfdGVzdF9hdXRvbWF0aW9uOkdyMzNuRG90IQ=='}
query = '''SELECT pg.ProgramCode, pd.ProductCode, pd.ProductName
FROM Product pd WITH (NOLOCK) 
INNER JOIN Program pg WITH (NOLOCK) ON pg.ProgramKey = pd.ProgramKey
WHERE pg.ProgramCode NOT IN ('ubervd', 'spark', 'intuittc', 'stash', 'lana', 'kabbage') ----- not used
AND pd.ProductCode NOT LIKE 'S%'AND pd.ProductCode NOT LIKE 'L%'
AND (pd.ProductName LIKE '%Debit%' OR pd.ProductName LIKE '%Credit%')
AND pd.ProductCode not in ('51600')
ORDER BY pd.ProductCode
'''
query_type = '''SELECT pg.ProgramCode, pd.ProductCode, pd.ProductName,
CASE
WHEN pd.ProductName LIKE '%Secured Credit Card%' THEN 'SCC'
ELSE 'DDA'
END ProductType
FROM Product pd WITH (NOLOCK) 
INNER JOIN Program pg WITH (NOLOCK) ON pg.ProgramKey = pd.ProgramKey
WHERE pg.ProgramCode NOT IN ('ubervd', 'spark', 'intuittc') ----- not used
AND pd.ProductCode NOT LIKE 'S%'AND pd.ProductCode NOT LIKE 'L%'
AND (pd.ProductName LIKE '%Debit%' OR pd.ProductName LIKE '%Credit%')'''

def find_product_config_runnable_session(program_code, proudct_code, session):
    url = "https://boscrmsvc.qa.uw2.gdotawsnp.com/CareMtApi/v1/api/programs/%s/allFeatures?ProductCode=%s" %(program_code, proudct_code)
    response = session.get(url,verify=False)
    error = ""
    responseMessage = ""
    if response.status_code != 200:
        error = "Url: %s ,Status code: %s" %(url, str(response.status_code))
        responseMessage = "{}"
    else:
        responseMessage = response.content.decode(Constant.UTF8) 
    print('Url %s response %s' % (url, str(response)))
    return responseMessage, error

def getContentsFromConf(team, reverse_list):
    res_map = {}
    page_Title = Project_Feature_Page_Title_Map[team]       
    testRailAPI_URL = Conf_Base_URL + '?title=' + page_Title + '&expand=body.storage'        
    req = urlequest.Request(url=testRailAPI_URL, headers=headers)
    res = urlequest.urlopen(req)
    res_str = str(res.read().decode('utf-8'))
    json_obj = json.loads(res_str)
    json_dict = json_obj['results'][-1]['body']['storage']['value']
    value_soup = BeautifulSoup(str(json_dict))
    table_values = value_soup.findAll('table')
    for table_value in table_values:
        res_dict=[]            
        table_name = table_value.find_previous_sibling().text
        table_value = ''.join(str(table_value).split('<thead>')).strip()
        table_value = ''.join(str(table_value).split('</thead>')).strip()
        table_value = ''.join(str(table_value).split('<tbody>')).strip()
        table_value = ''.join(str(table_value).split('</tbody>')).strip()
        table = et.fromstring(table_value)
        rows = iter(table)
        next(rows)
        if table_name in reverse_list:
            is_first_row = True
            for row in rows:
                is_first_col = True
                header_name = ''
                col_index = 0
                for col in row:
                    col_text = ''.join(col.itertext()).strip() if col.text is None else str(col.text).strip()
                    if is_first_col:
                        header_name = col_text
                        is_first_col = False
                    else:
                        if is_first_row:
                            res_dict.append({header_name:col_text})
                        else:
                            res_dict[col_index][header_name] = col_text
                            col_index += 1
                if is_first_row:
                    is_first_row = False
            res_map[table_name]=res_dict    
        else:
            table_headers = [''.join(col.itertext()).strip() if col.text is None else str(col.text).strip() for col in next(rows)]        
            for row in rows:
                values = [''.join(col.itertext()).strip() if col.text is None else str(col.text).strip() for col in row]
                res_dict.append(dict(zip(table_headers, values)))
            res_map[table_name]=res_dict
    return res_map

def getFeatureProductList(team):
    result = {}
    error_message = []
    if team not in Project_Feature_Page_Title_Map:
        return result, False, ["Failed to match team " + team]
    if team != 'ivr':
        api_result_map, product_list, error = getPruductConfigFromApi([])
    else:
        api_result_map = {}
        error = ''
    if error:
        error_message.extend(error)
    api_project_feature_map, product_code_feature_map_conf, is_conf_success, error_conf = processConfContent(team)
    if not is_conf_success:
        error_conf.extend(error_message)
        return result, False, error_conf   
    is_success = True 
    for product_code in api_result_map:
        if 'featureInfoList' not in api_result_map[product_code]:
            continue
        if product_code in product_code_feature_map_conf and 'GetFeaturesAPI' in product_code_feature_map_conf[product_code]:
            if product_code_feature_map_conf[product_code]['GetFeaturesAPI'].strip().lower() != 'true':
                continue            
        for feature_info in api_result_map[product_code]['featureInfoList']:
            if feature_info['isValid']:              
                feature_names =  api_project_feature_map[feature_info['feature']] if feature_info['feature'] in api_project_feature_map else [feature_info['feature']]
                for feature_name in feature_names:
                    appendToMapListByKey(result, feature_name, product_code)
    for product_code in product_code_feature_map_conf:
        feature_info_map = product_code_feature_map_conf[product_code]  
        for feature_name in feature_info_map:
            if not feature_name:
                continue;
            if feature_info_map[feature_name] == 'true':
                appendToMapListByKey(result, feature_name, product_code)
            elif feature_info_map[feature_name] == 'false':
                if feature_name in result and product_code in result[feature_name]:
                    result[feature_name].remove(product_code) 
    for feature_name in result:
        result[feature_name].sort()
    return OrderedDict(sorted(result.items(), key=lambda kv: kv[0])), is_success, error_message

def getPruductConfigFromApi(pcode_list):
    product_list = ProductDB().dbQuery(query)
    if pcode_list:
        product_list = [product for product in product_list if product['ProductCode'].strip() in pcode_list]
    api_result_map = {}
    error_message = []
    session = requests.Session()
    session.auth =HttpNtlmAuth("nextestate\\svc_QA_V3Test","Greendot1", session)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future_to_url = {executor.submit(find_product_config_runnable_session, product['ProgramCode'], product['ProductCode'], session): product for product in
                             product_list}
            for future in concurrent.futures.as_completed(future_to_url):
                product_info = future_to_url[future]
                data, error = future.result()
                if error:
                    error_message.append(error)
                api_result_map[product_info['ProductCode']] = json.loads(data)
                print('Finished to process %s' % (product_info))    
    return api_result_map, product_list, error_message

def processConfContent(team):
    is_success = True
    message = []
    if team not in Project_Feature_Page_Title_Map:
        return {},{}, False, ["Failed to match team " + team]
    if team == 'care_ui':
        table_map = getContentsFromConf(team, ['ProductCode Feature Table'])
        config_table_name = 'ProductCode Feature Table'
    else:
        table_map = getContentsFromConf(team, [])
        config_table_name = 'Feature ProductCode Table'
    product_code_feature_map_conf = {}
    api_project_feature_map = {}
    if "Features Mapping" in table_map:
        featureMapList = table_map["Features Mapping"]
        if featureMapList:
            project_headers = [header for header in featureMapList[0] if 'map' in header.lower()]
            if not project_headers:
                message.append("Failed to find project mapping header in table Features Mapping, should contains map")
                return {},{}, False, message;
            if 'API Feature Name' not in featureMapList[0]:
                message.append("Failed to find [API Feature Name] header in table Features Mapping")
                return {},{}, False, message;
            project_header = project_headers[0]
            for featureMap in featureMapList:
                if featureMap[project_header]:
                    if team == 'care_ui' and ',' in featureMap[project_header]:
                        api_project_feature_map[featureMap['API Feature Name']] = [x.strip() for x in featureMap[project_header].split(',')]
                    else:
                        api_project_feature_map[featureMap['API Feature Name']] = [featureMap[project_header]]
    else:
        message.append('Features Mapping table does not exist')
    if config_table_name in table_map:
        productCodeFeatureList = table_map[config_table_name]
        if productCodeFeatureList:
            if 'ProductCode' not in productCodeFeatureList[0]:
                message.append("Failed to find [ProductCode] header in table [" + config_table_name + "]")
                return {},{}, False, message
            for productCodeFeature in productCodeFeatureList:
                if productCodeFeature['ProductCode'] != "":
                    product_code_feature_map_conf[productCodeFeature['ProductCode']] = productCodeFeature
    else:
        message.append(config_table_name + ' does not exist')
        return {}, {}, False, message
    return api_project_feature_map, product_code_feature_map_conf, is_success, message


def updateConfPage(pcode_list, team, is_preview):
    result = {}
    error_message = []
    is_success = True
    if not team:
        team = 'care'
    if team not in Project_Feature_Page_Title_Map:
        return result, False, ["Failed to match team " + team]
    api_result_map, product_list, error = getPruductConfigFromApi(pcode_list)
    error_message.extend(error)
    api_project_feature_map, product_code_feature_map_conf, is_conf_success, error_conf = processConfContent(team)
    if not is_conf_success:
        return result, False, [error_conf].extend(error)  
    ptype_list = ProductDB().dbQuery(query_type)
    ptype_map = {}
    for ptype in ptype_list:
        ptype_map[ptype['ProductCode']] = ptype['ProductType']
    for pcode in api_result_map:
        if 'featureInfoList' in api_result_map[pcode]:
            ptype = ptype_map[pcode]
            if team == 'care_ui':
                feature_name = 'SCC Common' if ptype == 'SCC' else 'DDA Common'
            else:               
                feature_name = 'CommonCase_SCC' if ptype == 'SCC' else 'CommonCase' 
            api_result_map[pcode]['featureInfoList'].append({"feature": feature_name, "isValid": True})
    conf_URL = Conf_Base_URL + '?title=' + Project_Feature_Page_Title_Map[team.lower()] + '&expand=body.storage,version'       
    req = urlequest.Request(url=conf_URL, headers=headers)
    res = urlequest.urlopen(req)
    res_str = str(res.read().decode('utf-8'))
    json_obj = json.loads(res_str)
    json_dict = json_obj['results'][-1]['body']['storage']['value']
    regex = re.compile(r'<!\[CDATA\[(.+?)\]\]>', re.DOTALL)
    inputData = regex.sub(r'X![CDATA[\1]]X', str(json_dict))
    value_soup = BeautifulSoup(str(inputData))
    table_values = value_soup.findAll('table')
    update_message_map = {}
    add_message_map = {}
    for table_value in table_values:            
        table_name = table_value.find_previous_sibling().text
        if table_name == 'ProductCode Feature Table':
            rows = table_value.find_all('tr')
            pcode_index_map = {}
            index_pcode_map = {}
            header_index_map = {}
            header_index = 0
            is_first_col = True
            first_col = 'N/A'
            enable_api_index_list = []
            for header_row in table_value.findAll("th"):
                if is_first_col:                           
                    first_col = header_row.text.strip()
                    is_first_col = False
                header_index_map[header_row.text]= header_index
                header_index += 1
            first_td_cols = []
            for row in rows:
                cols = row.find_all('td')
                if not cols:
                    continue
                if cols[0].text.strip() in first_td_cols:
                    error_message.append("Duplicate first column [%s] detected." %(cols[0].text.strip()))          
                    return "N/A", False, error_message 
                first_td_cols.append(cols[0].text.strip())   
                if cols[0].text.strip() == 'ProductCode':
                    header_index = 0
                    for col in cols:
                        col_text = col.text.strip()
                        if col_text != 'ProductCode' and col_text != '' and col_text in pcode_list:
                            pcode_index_map[col_text]= header_index
                            index_pcode_map[header_index] = col_text
                            pcode_list.remove(col_text)  
                        header_index += 1
                if cols[0].text.strip() == 'GetFeaturesAPI':
                    header_index = 0
                    for col in cols:
                        col_text = col.text.strip()
                        if col.text.strip() == 'true' :
                            enable_api_index_list.append(header_index)
                        header_index += 1
            enable_api_pcode_list = []
            if index_pcode_map and enable_api_index_list:
                for index in enable_api_index_list:
                    if index in index_pcode_map:
                        enable_api_pcode_list.append(index_pcode_map.get(index))

            feature_valid_product_index_map = {}
            for product_code in pcode_index_map:
                if product_code not in enable_api_pcode_list:
                    continue
                if product_code in api_result_map and 'featureInfoList' in api_result_map[product_code]:
                    for feature_info in api_result_map[product_code]['featureInfoList']:
                        if feature_info['isValid']:
                            feature_names =  api_project_feature_map[feature_info['feature']] if feature_info['feature'] in api_project_feature_map else [feature_info['feature']]
                            for feature_name in feature_names:
                                appendToMapListByKey(feature_valid_product_index_map, feature_name, pcode_index_map[product_code])
            for row in rows:
                cols = row.find_all('td')
                if not cols:
                    continue
                if cols[0].text.strip() in ['ProgramCode','ProductCode','GetFeaturesAPI']:
                    continue 
                feature_name = cols[0].text.strip()
                if feature_name in feature_valid_product_index_map:
                    for valid_product_index in feature_valid_product_index_map[feature_name]:
                        if cols[valid_product_index].text.strip() != 'true':
                            cols[valid_product_index].string = 'true'
                            appendToMapListByKey(update_message_map, feature_name, index_pcode_map[valid_product_index] + '=true')
                                                  
            feature_value_list_map = {}                
            common_index = None
            if 'DDA_Common' in header_index_map:
                common_index =  header_index_map['DDA_Common']                
            
            for product_code in pcode_list:                   
                if product_code in api_result_map and 'featureInfoList' in api_result_map[product_code]:
                    feature_names_covered = []
                    for feature_info in api_result_map[product_code]['featureInfoList']:
                        if feature_info['isValid']:
                            col_value = 'true' 
                        else:
                            col_value = '' 
                        feature_names =  api_project_feature_map[feature_info['feature']] if feature_info['feature'] in api_project_feature_map else [feature_info['feature']]
                        for feature_name in feature_names:
                            feature_names_covered.append(feature_name)
                            appendToMapListByKey(feature_value_list_map, feature_name, col_value)
                            appendToMapListByKey(add_message_map, feature_name, product_code + '=true')
                        
                                   
                    program_code = next((product['ProgramCode'] for product in product_list if product['ProductCode'].strip()== product_code), "N/A")
                    for row in rows:
                        cols = row.find_all('td')
                        if not cols:
                            continue
                        if cols[0].text.strip() in ['ProgramCode','ProductCode','GetFeaturesAPI'] or cols[0].text.strip() in feature_names_covered:
                            continue
                        appendToMapListByKey(feature_value_list_map, cols[0].text.strip(), '')
                    appendToMapListByKey(feature_value_list_map, first_col, program_code)
                    appendToMapListByKey(feature_value_list_map, 'ProgramCode', program_code)
                    appendToMapListByKey(feature_value_list_map, 'ProductCode', product_code)
                    appendToMapListByKey(feature_value_list_map, 'GetFeaturesAPI', 'true')
                              
            if feature_value_list_map:                   
                for row in rows:
                    cols = row.find_all('td')
                    tag_name = 'td'
                    if not cols:
                        cols = row.find_all('th')
                        if cols:
                            tag_name = 'th'
                        else:
                            continue
                    last_new_td = None     
                    for col_value in feature_value_list_map.get(cols[0].text.strip(),[]):                                      
                        if common_index:
                            new_td = value_soup.new_tag(tag_name, attrs=cols[common_index].attrs)
                            new_td.string = col_value
                            if not last_new_td:
                                cols[common_index].insert_before(new_td)
                            else:
                                last_new_td.insert_after(new_td) 
                            last_new_td = new_td
                        else:
                            new_td = value_soup.new_tag(tag_name, attrs=cols[-1].attrs)
                            new_td.string = col_value
                            if not last_new_td:
                                cols[-1].insert_after(new_td)
                            else:
                                last_new_td.insert_after(new_td) 
                            last_new_td = new_td
                
        if table_name == 'Feature ProductCode Table':
            header_index_map = {}
            header_index = 0
            for header_row in table_value.findAll("th"):
                header_index_map[header_row.text]= header_index
                header_index += 1
            rows = table_value.find_all('tr')
            last_row = None
            new_tr = None
            for row in rows:
                cols = row.find_all('td')
                if not cols:
                    continue
                if (cols[header_index_map['ProductCode']].text.strip() in pcode_list and cols[header_index_map['GetFeaturesAPI']].text.strip() == "true"):                
                    product_code = cols[header_index_map['ProductCode']].text.strip()
                    if product_code in api_result_map and 'featureInfoList' in api_result_map[product_code]:
                        for feature_info in api_result_map[product_code]['featureInfoList']:
                            if feature_info['isValid']:              
                                feature_names =  api_project_feature_map[feature_info['feature']] if feature_info['feature'] in api_project_feature_map else [feature_info['feature']]
                                for feature_name in feature_names:
                                    if feature_name in header_index_map:
                                        if cols[header_index_map[feature_name]].text.strip() != 'true':
                                            cols[header_index_map[feature_name]].string = 'true'
                                        appendToMapListByKey(update_message_map, product_code, feature_name + '=true')
                if cols[header_index_map['ProductCode']].text.strip() in pcode_list:
                    pcode_list.remove(cols[header_index_map['ProductCode']].text.strip())       
                last_row = row
            for pcode in pcode_list:              
                new_tr = value_soup.new_tag('tr', attrs=last_row.attrs)
                cols = last_row.find_all('td')
                for col in cols:
                    new_td = value_soup.new_tag('td', attrs=col.attrs)
                    new_td.string = ""
                    new_tr.append(new_td)
                cols = new_tr.find_all('td')
                if pcode in api_result_map and 'featureInfoList' in api_result_map[pcode]:
                    cols[header_index_map['ProductCode']].string = pcode
                    program_code = next((product['ProgramCode'] for product in product_list if product['ProductCode'].strip()== pcode), "N/A")
                    cols[header_index_map['ProgramCode']].string = program_code
                    cols[header_index_map['GetFeaturesAPI']].string = 'true'
                    for feature_info in api_result_map[pcode]['featureInfoList']:
                        if feature_info['isValid']:              
                            feature_names =  api_project_feature_map[feature_info['feature']] if feature_info['feature'] in api_project_feature_map else [feature_info['feature']]
                            for feature_name in feature_names:
                                if feature_name in header_index_map:
                                    cols[header_index_map[feature_name]].string = 'true'
                                    appendToMapListByKey(add_message_map, pcode, feature_name + '=true')
                last_row.append(new_tr)
                last_row = new_tr
    
    preview_status = '(preview)' if is_preview else ''
    if update_message_map:
        result['Update rows' + preview_status] = update_message_map
    if add_message_map:
        result['Add rows' + preview_status] = add_message_map
    if len(update_message_map) == 0 and len(add_message_map) == 0 and not is_preview:
        error_message.append("Skip to update as no items need to change or add.")    
    elif not is_preview:
        body =  { "storage": { 
                                 "value": value_soup.body.decode_contents().replace('X![','<![').replace(']]X',']]>') ,
                                 "representation": "storage" 
                            }
                 }
        post_field_data = { "version" : { "number": json_obj['results'][-1]['version']['number'] + 1 },
                "title": json_obj['results'][-1]["title"] ,
                "type": json_obj['results'][-1]["type"],
                "body": body }
        put_url = Conf_Base_URL + "/" + str(json_obj['results'][-1]['id'])
        response = requests.put(put_url, json=post_field_data,headers=headers_put,verify=False)
        if response.status_code != 200:
            error_message.append("Failed to update Url: %s ,Status code: %s, Team %s" %(put_url, str(response.status_code), team))          
            return "N/A", False, error_message
    return result, is_success, error_message
def appendToMapListByKey(map_obj, key, value_to_append):
    if key in map_obj:
        if value_to_append not in map_obj[key]:
            map_obj[key].append(value_to_append )
    else:
        map_obj[key] = [value_to_append]