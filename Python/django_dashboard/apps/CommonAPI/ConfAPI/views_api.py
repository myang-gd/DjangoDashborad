from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import feature_helper
import traceback

class FeatureConfig(APIView):
    def get(self, request, format=None):
        try:
            if  "team" in request.GET: 
                if request.GET['team'].strip() == '':
                    return Response({"items":[], "is_success":"False", "message":"Invalid team name" + str(request.GET['team'])}, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    team = request.GET['team'].strip()
            else:
                team = 'care'
            feature_prodcut_list_map, is_success, message_info = feature_helper.getFeatureProductList(team)
        except Exception as e:
            trace = "\n" + traceback.format_exc() if 'debug' in request.GET else ""
            return Response({"items":[], "is_success":"False", "message":str(e) + trace}, status=status.HTTP_400_BAD_REQUEST)
        else:            
            return Response({"items":feature_prodcut_list_map, "is_success":str(is_success), "message":message_info}, status=status.HTTP_200_OK)

class UpdateConfFeatureConfig(APIView):
    def get(self, request, format=None):
        pcode_list = []
        is_preview = True
        if "pcode_list" in request.GET:
            pcode_list = [x.strip() for x in request.GET['pcode_list'].split(',')]
            if not pcode_list:
                return Response({"result":"", "is_success":"False", "message":"Failed get product id from " + str(request.GET['pcode_list'])}, status=status.HTTP_400_BAD_REQUEST)    
        else:
            return Response({"result":"", "is_success":"False", "message":"pcode_list with comma as delimiter is not provided." }, status=status.HTTP_400_BAD_REQUEST) 
        if "is_preview" in request.GET and request.GET['is_preview'].lower() == 'false':
            is_preview =  False
        if  "team" in request.GET: 
            if request.GET['team'].strip() == '':
                return Response({"result":"", "is_success":"False", "message":"Invalid team name" + str(request.GET['team'])}, status=status.HTTP_400_BAD_REQUEST) 
            else:
                team = request.GET['team'].strip()
        else:
            team = 'care'
        try:
            result, is_success, error = feature_helper.updateConfPage(pcode_list, team, is_preview)
        except Exception as e:
            trace = "\n" + traceback.format_exc() if 'debug' in request.GET else ""
            return Response({"result":"", "is_success":"False", "message":str(e) + trace}, status=status.HTTP_400_BAD_REQUEST)
        else:            
            return Response({"result":result, "is_success":str(is_success), "message":error}, status=status.HTTP_200_OK)