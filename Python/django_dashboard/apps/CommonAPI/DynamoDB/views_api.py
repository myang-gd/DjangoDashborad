from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3

class Query(APIView):
    def post(self, request, format=None):
        if 'table' not in request.data or 'expression' not in request.data or 'values' not in request.data:
            return Response({"items":[], "result":"fail", "message":"table/expression/values should include in the request"}, status=status.HTTP_400_BAD_REQUEST)       
        region_name='us-west-2'
        service_name = 'dynamodb'
        env = "dynamodb"
        try:
            session = boto3.Session(profile_name=env.lower())  
            client = session.client(service_name,region_name=region_name)      
            response = client.query(
                TableName= request.data['table'],
                KeyConditionExpression=request.data['expression'],
    
                ExpressionAttributeValues=request.data['values']
            )
        except Exception as e:
            return Response({"items":[], "result":"failed", "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"items":response['Items'],"length":len(response['Items']), "result":"success", "message":""}, status=status.HTTP_200_OK)
       
