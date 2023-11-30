from django.shortcuts import render
from apps.License.utils import LicenseDB
from common_utils.ldap_util import LdapUtil
import urllib.request as urlequest
import xml.etree.ElementTree as et
import json
from bs4 import BeautifulSoup 
import requests
from requests_ntlm import HttpNtlmAuth
from django.http import HttpResponseNotAllowed
from common_utils.ws_util import WSUtil
from common_utils.constant import Constant
import datetime
import concurrent.futures

query = '''SELECT  *
  FROM [LicenseServer].[dbo].[License] where UserId is null and ExpirationDate > GETDATE()-2
'''
query_pending_approve = '''SELECT  License.*, Users.Name, Users.UserName, Users.Team
  FROM License inner join Users on Users.UserId = License.UserId
  where License.UserId is not null and Activated = 0 and Approved = 0 and ExpirationDate > GETDATE()-2'''
query_pending_activate = '''SELECT  License.*, Users.Name, Users.UserName, Users.Team
  FROM License inner join Users on Users.UserId = License.UserId
  where License.UserId is not null and Activated = 0 and Approved = 1 and ExpirationDate > GETDATE()-2'''
query_existing_for_user = '''SELECT License.*
  FROM License inner join 
  Users on Users.UserId = License.UserId
  where Users.UserName = '''
headers = {'Authorization' : 'Basic cWFfdGVzdF9hdXRvbWF0aW9uOkdyMzNuRG90IQ=='}

def license(request, template="license/overview.html"):
    licenses = LicenseDB().dbQuery(query)
    pending_activate_licenses = LicenseDB().dbQuery(query_pending_activate)
    pending_approve_licenses = LicenseDB().dbQuery(query_pending_approve)
    total_left = len(licenses)
    count_by_date = {}
    for license in licenses:
        expDate = license['ExpirationDate']
        if expDate:
            if expDate in count_by_date:
                count_by_date[expDate] += 1
            else:
                count_by_date[expDate] = 1
    context = {'total_left':str(total_left)}
    if count_by_date:
        context['count_by_date'] = count_by_date
        
    pending_activate_info, pending_activate_total = get_pending_info(pending_activate_licenses)
    if pending_activate_info:
        context['pending_activate_info'] = pending_activate_info
    context['pending_activate_total']  = pending_activate_total
    
    pending_approve_info, pending_approve_total = get_pending_info(pending_approve_licenses)
    if pending_activate_info:
        context['pending_approve_info'] = pending_approve_info
    context['pending_approve_total']  = pending_approve_total
                   
    return render(request, template, context)
def get_user(request, template="license/check_user.html"):
    user = ''
    if request.method == 'POST':
        user = request.POST.get('user')
        if '@' in user:
            user = user.split('@', 1)[0]        
    elif request.method == 'GET':
        return render(request, template, {})
    else:
        return HttpResponseNotAllowed(request.method)
    if not user:
        return render(request, template, {})
    existing_licenses = LicenseDB().dbQuery(query_existing_for_user + "\'" + user + "\'")
    res_map = getContentsFromConf('https://wiki.nextestate.com/rest/api/content?title=ReadyAPI+-+License+Allocation+(Contractors)&spaceKey=QAAR')
    existing_licenses_conf = []
    if 'default' in res_map and res_map['default']:
        for licene_row in  res_map['default']:
            if user.strip().lower() == licene_row['Email'].split('@', 1)[0].strip().lower():
                existing_licenses_conf.append(licene_row)
               
    groups =  LdapUtil.getUserGroupNames(user)
    account_expires =  LdapUtil.getUserExpires(user)
    if account_expires == '0':
        expires_date = 'Never'
    else:
        expires_date = str(nanoToDate(account_expires))
    contractor_groups = []
    for group in groups:
        if 'contractor' in group.lower():
            contractor_groups.append(group)
    context = {}
    context['expires_date'] = expires_date
    context['groups'] = groups
    context['user_name'] = user
    context['contractor_groups'] = ' ,'.join(contractor_groups) if contractor_groups else 'Empty'
    context['contractor_groups'] = 'N/A' if not groups else context['contractor_groups']
    if existing_licenses:
        context['existing_licenses'] = existing_licenses
    if existing_licenses_conf:
        context['existing_licenses_conf'] = existing_licenses_conf
    return render(request, template, context)
def check_disable_account(request, template="license/check_disable_account.html"):
    context = {}
    if request.method != 'POST':
        return render(request, template, context)
    conf_option = request.POST.get('conf_option')
    if conf_option == '1':
        title = 'ReadyAPI+-+License+Allocation+(Contractors)'
    elif conf_option == '2':
        title = 'ReadyAPI+-+License+Allocation+(DEV)'
    else:
        title = 'ReadyAPI+-+License+Allocation+(Contractors)'
    url_conf = 'https://wiki.nextestate.com/rest/api/content?spaceKey=QAAR&title=' + title
    res_map = getContentsFromConf(url_conf)  
    disabled_user_licenses = []
    unknown_user_licenses = []
    if 'default' in res_map and res_map['default']:      
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(LdapUtil.getUserAccountControl, licene_row['Email'].split('@', 1)[0].strip()): licene_row for licene_row in  res_map['default'] if licene_row['Email'].split('@', 1)[0].strip() != ''}
            for future in concurrent.futures.as_completed(future_to_url):
                licene_row_input = future_to_url[future]
                try:
                    account_status = future.result()
                    if account_status in ['546', '514']:
                        disabled_user_licenses.append(licene_row_input)
                    elif account_status == 'N/A':
                        unknown_user_licenses.append(licene_row_input)
                except Exception as exc:
                    print('%s generated an exception: %s' % (str(licene_row_input['Email']), exc)) 
                else:
                    print('Finished to process %s' % (str(licene_row_input['Email'])))        

    if disabled_user_licenses:
        context['disabled_user_licenses'] =  disabled_user_licenses
    if unknown_user_licenses:
        context['unknown_user_licenses'] =  unknown_user_licenses
    return render(request, template, context)
def check_free_license(request, template="license/check_free_license.html"):
    context = {}
    if request.method != 'POST':
        return render(request, template, context)
    conf_option = request.POST.get('conf_option')
    p4_files = []
    nameBase = 'soapUI-license-SO00125234-2-'
    target = 'QA'
    if conf_option == '1':
        title = 'ReadyAPI+-+License+Allocation+(Contractors)'
        for x in range(1,101):# 1-100
            p4_files.append(nameBase+str(x)+'.key')
    elif conf_option == '2':
        target = 'DEV'
        for x in range(101,151):# 101-150
            p4_files.append(nameBase+str(x)+'.key')
        title = 'ReadyAPI+-+License+Allocation+(DEV)'
    else:
        title = 'ReadyAPI+-+License+Allocation+(Contractors)'
    url_conf = 'https://wiki.nextestate.com/rest/api/content?spaceKey=QAAR&title=' + title
    res_map = getContentsFromConf(url_conf)  
    free_licenses = []
    free_licenses_conf = []
    pending_license_request = []
    emails = []
    dup_emails = []
    licenses = []
    dup_licenses = []
    if 'default' in res_map and res_map['default']: 
        for licene_row in  res_map['default']:
            license = licene_row['License'].strip() if 'License' in licene_row else ''
            name = licene_row['Name'].strip() if 'Name' in licene_row else ''
            email = licene_row['Email'].strip() if 'Email' in licene_row else ''
            if email != '':
                if email not in emails:         
                    emails.append(email)
                else:
                    dup_emails.append(email)
            if license != '':
                if license not in licenses:         
                    licenses.append(license)
                else:
                    dup_licenses.append(license)            
            if license != '' and name == '' :
                free_licenses_conf.append(licene_row)
            if license != '' and license in p4_files:
                p4_files.remove(license) 
            if (name != '' or email != '') and license == '':
                pending_license_request.append(licene_row)
    for p4_file in p4_files:
        free_licenses.append({'License':p4_file})       
    if free_licenses:
        context['free_licenses'] =  free_licenses
    if free_licenses_conf:
        context['free_licenses_conf'] =  free_licenses_conf
    total_license = len(free_licenses) + len(free_licenses_conf)
    if free_licenses_conf or free_licenses_conf:     
        context['total'] = str(total_license)
        context['target'] = str(target)
    if dup_emails:
        context['dup_emails'] =  dup_emails
    if dup_licenses:
        context['dup_licenses'] =  dup_licenses
    if pending_license_request:
        context['pending_license_request'] =  pending_license_request
    return render(request, template, context)
def encrypt(request, template="license/encrypt.html"):
    encode_decode_string = ''
    if request.method == 'POST':
        encode_decode_string = request.POST.get('encode_decode_string')     
    elif request.method == 'GET':
        return render(request, template, {})
    else:
        return HttpResponseNotAllowed(request.method)
    if not encode_decode_string:
        return render(request, template, {})
    context = {}
    url = "http://GDCQATOOLS01:8089/ReadyAPI_MSSQL_Engine/Encrypt"
    request_msg = {"encode_decode_string":encode_decode_string}
    result = WSUtil.processRestRequest(url=url, message=json.dumps(request_msg), method='POST')
    if Constant.ERROR in result and result.get(Constant.ERROR):
        result_str = result.get(Constant.ERROR)
    else:
        result_str = result.get(Constant.TEXT)
        
    context['result'] = result_str.strip('"')
    return render(request, template, context);

def get_pending_info(pending_licenses):
    pending_info = {}
    pending_total = 0
    for license in pending_licenses:
        user_id = license['UserId']
        if user_id not in pending_info:
            pending_info[user_id] = {'Name':license['Name'],'UserName':license['UserName'],'Team':license['Team'],
                  'ManagerEmail':license['ManagerEmail'], 'Count':1}
        else:
            pending_info[user_id]['Count'] += 1
        pending_total += 1
    
    return pending_info, pending_total
 

def getContentsFromConf(url):
    res_map = {}      
    testRailAPI_URL = url + '&expand=body.view'        
    req = urlequest.Request(url=testRailAPI_URL, headers=headers)
    res = urlequest.urlopen(req)
    res_str = str(res.read().decode('utf-8'))
    json_obj = json.loads(res_str)
    #json_dict = json_obj['results'][-1]['body']['storage']['value']
    json_dict = json_obj['results'][-1]['body']['view']['value']
    value_soup = BeautifulSoup(str(json_dict))
    table_values = value_soup.findAll('table')
    for table_value in table_values:
        res_dict=[]            
        table_name = table_value.find_previous_sibling().text if table_value.find_previous_sibling() else 'default'
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
        res_map[table_name]=res_dict
    return res_map

def nanoToDate(nano_time):
    try:
        seconds = int(nano_time) / 10000000
        epoch = seconds - 11644473600 
        dt = datetime.datetime(2000, 1, 1, 0, 0, 0)
        result = dt.fromtimestamp(epoch)
    except Exception as e:
        result = 'N/A'
    finally:
        return result
    
    
