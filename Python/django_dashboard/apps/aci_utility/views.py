from django.http import HttpResponse
from django.shortcuts import render
import json

from common_utils.card_retriever_db import CardRetrieverdbDatabase


def aci_utility(request):
    return render(request, 'aci_utility.html')


def get_aci_card_info(request):
    if request.is_ajax():
        pts_card_info = []

        env = request.POST.get('env')
        serial_nbr = request.POST.get('serial_nbr')
        isPersonalized = request.POST.get('isPersonalized')

        if env != "Environment" and serial_nbr != "":
            crd = CardRetrieverdbDatabase()
            pts_card_info = crd.aci_cardinfo_sp(env, serial_nbr, isPersonalized)

        output = {'PTSCardInfo': pts_card_info, 'Error': '', 'ResponseCode': '200'}
        return HttpResponse(json.dumps({'Output': output}), content_type='application/json')
    else:
        pass