import requests
from django.http import HttpResponse
from django.shortcuts import render
import json

url_recent_apps = "https://api-cloud.browserstack.com/app-automate/recent_apps?limit=300"
url_recent_group_apps = "https://api-cloud.browserstack.com/app-automate/recent_group_apps?limit=300"
url_delete = "https://api-cloud.browserstack.com/app-automate/app/delete/"

headers = {
    "Authorization": "Basic YXV0b21hdGlvbm1vYmlsZXhFeUVDOjRBaGFYZnhxTVpoenJUY015TXZu",
}

def apps(request):

    if not request.is_ajax():
        response = requests.get(url_recent_apps, headers = headers)
        jsonArrayAuto = response.json()
        response = requests.get(url_recent_group_apps, headers = headers)
        jsonArrayAll = response.json()

        for app in jsonArrayAll:
            if any(item['app_id'] == app['app_id'] for item in jsonArrayAuto):
                app['removable'] = True

        context = { 'app_list': jsonArrayAll }
        return render(request, 'apps.html', context)
    else:
        action = request.POST.get('action')
        target = url_delete + request.POST.get('app_id')
        if action == "delete":
            response = requests.delete(target, headers = headers)
            jsonArray = response.json()
            if jsonArray["success"] == True:
                return HttpResponse(json.dumps({'Output': "Success"}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'Output': "Fail"}), content_type='application/json')

