
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CurrentLocks, Servers, GdUser, Fields, Environments,Filemap,ServerTypes,SuspendActivity, ValueTypes, ServerTypes
from common_utils.django_util import Django_Util
from . import serializers
import datetime
from common_utils.str_util import StrUtil
import socket
from dns import resolver

APP_LABEL = 'ConfigModifier'
CURRENTLOCKS = 'CurrentLocks'
SERVERS = 'Servers'
GDUSER = 'GdUser'
FIELDS = 'Fields'
ENVIRONMENTS = 'Environments'
FILEMAP = 'Filemap'
SERVERTYPES = 'ServerTypes'
SUSPENDACTIVITY = 'SuspendActivity'
SERVER_ID = 'server_id'
FIELD_ID = 'field_id'
ENVIRONMENT_ID = 'environment_id'

field_delay_map = {}

def getFields(attrs):   
        server_name = attrs.get(serializers.SERVER_NAME,None)
        file = attrs.get(serializers.FILE,None)     
        config = attrs.get(serializers.CONFIG,None)    
        element_path = attrs.get(serializers.ELEMENT_PATH,None)    
        attribute = attrs.get(serializers.ATTRIBUTE,None) 
        server_id = attrs.get(serializers.SERVER_ID,None) 
        server_type = attrs.get(serializers.SERVER_TYPE,None)
        fields = Fields.objects.all()
    
        filemaps = None;
        include_filemaps = False;
        if file:
            index = file.rfind('\\')
            file_name = file[(index+1):]
            location = file[:index]
        else:
            file_name = None
            location = None
        if file_name:
            filemaps = Filemap.objects.filter(filename__iexact=file_name.strip())
            include_filemaps = True;
        else:
            filemaps = Filemap.objects.all()            
        if location: 
            include_filemaps = True;
            filemaps = filemaps.filter(location__iexact=location.strip())                    
        if server_name:
            server = Servers.objects.filter(server_name__iexact=server_name.strip()).first()
            include_filemaps = True;
            filemaps = filemaps.filter(server_type=(server.server_type if server else None))
        elif server_id:
            server = Servers.objects.get(id=server_id)
            include_filemaps = True;
            filemaps = filemaps.filter(server_type=(server.server_type if server else None))
        elif server_type:
            include_filemaps = True;
            filemaps = filemaps.filter(server_type=ServerTypes.getByName(server_type))
                                                       
        if include_filemaps:
            fields = fields.filter(file_id__in=filemaps)            
        if element_path:
            fields = fields.filter(element_path=element_path.strip()) 
        if attribute:
            fields = fields.filter(attribute=attribute.strip()) 
        if config:
            fieldIdList = [field.id for field in fields if config.strip() == ("%s%s" %(field.display,((" %s="%(field.attribute)) if field.attribute else "" ))).strip()]
        else:
            fieldIdList = [field.id for field in fields]
            
        return  fields.filter(id__in=fieldIdList)
def getUniqueFieldId(attrs):         

    response = None
    field_id = None

    server_name = attrs.get(serializers.SERVER_NAME,None)
    environment_name = attrs.get(serializers.ENVIRONMENT_NAME,None)
    
    if server_name and environment_name:
        servers = Servers.objects.filter(server_name=server_name)
        if len(servers) > 1:
            found = False
            for server in servers:
                if str(server.environment_id) == environment_name.strip():
                    found = True
                    break
            if not found:
                response = {'error': "Server name and environment name does not match"}  
                return field_id, response 
        else:              
            server = servers.first()
            if not server:
                response = {'error': "Server name is invalid"}  
                return field_id, response 
            elif server and str(server.environment_id) != environment_name.strip():
                response = {'error': "Server name and environment name does not match"}  
                return field_id, response 
    fields = getFields(attrs)
    
    if len(fields) == 0:
        response = {'error': "Can't find field"} 
        return field_id, response   
    if len(fields) != 1:
        response = {'error': "Can't find unique field"} 
        return field_id, response  
    field_id = fields.first().id
    return field_id, response  

    
# def getUniqueFieldIdByAttrs(attrs):         
#     server_name = attrs.get(serializers.SERVER_NAME)
#     environment_name = attrs.get(serializers.ENVIRONMENT_NAME)
#     filename = attrs.get(serializers.FILENAME)   
#     location = attrs.get(serializers.LOCATION) 
#     display = attrs.get(serializers.DISPLAY)   
#     element_path = attrs.get(serializers.ELEMENT_PATH) 
#     attribute = attrs.get(serializers.ATTRIBUTE)
#     
#     return getUniqueFieldId(server_name=server_name,environment_name=environment_name,
#                           filename=filename,location=location,display=display,element_path=element_path,attribute=attribute)


def get_object(pk, appLabel, modelName):
        try:
            _model = Django_Util.getModel(appLabel, modelName)
            if not _model:
                raise Http404
            return _model.objects.get(pk=pk)
        except _model.DoesNotExist:
            raise Http404
      
class CurrentLocksList(APIView):
    """
    List all CurrentLocks, or create a new CurrentLock.
    """
    def get(self, request, format=None):
        error_response,currentLocks = self.getCurrentLocksByFilters(request)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        currentLocks = currentLocks.order_by('-requesttime')[:50]
        serializer = serializers.CurrentLocksSerializer(currentLocks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        fillServerNameError,is_multi = self.fillServerNames(request)
        if fillServerNameError:
            return Response(fillServerNameError, status=status.HTTP_400_BAD_REQUEST)
        if is_multi:
            serializer_list = []
            serializer_data_list = []
            for server_id in request.data[serializers.SERVER_IDS]:
                request.data[serializers.SERVER_ID] = server_id
                error_response, re_status= self.fillIds(request)
                if error_response:
                    return Response(error_response, status=re_status)
                serializer = serializers.CurrentLocksSerializer(data=request.data)
                if serializer.is_valid():
                    serializer_list.append(serializer)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            for serializer_obj in serializer_list:
                serializer_obj.save()
                serializer_data_list.append(serializer_obj.data)
            self.set_field_delay(request)
            return Response(serializer_data_list, status=status.HTTP_201_CREATED)
        error_response, re_status= self.fillIds(request)
        if error_response:
            return Response(error_response, status=re_status)
        self.set_field_delay(request)
        serializer = serializers.CurrentLocksSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def getServerIdByFieldandEnv(self, field_id, environment_id):       
        server_id = None
        field = Fields.objects.filter(id=field_id).first()
        if field and field.file_id and field.file_id.server_type:
            server = Servers.objects.filter(server_type=field.file_id.server_type, environment_id=environment_id).first()
            if server:
                server_id = server.id
        
        return   server_id
    def set_field_delay(self, request):      
        if request and serializers.FIELD_ID in request.data:
            field_delay_map[serializers.FIELD_ID] = datetime.datetime.now()
    def fillServerNames(self, request):
        data=request.data
        error_response = None
        server_id_list = []
        is_multi = False
        if serializers.INCLUDE_ALL_SERVERS in data and data.get(serializers.INCLUDE_ALL_SERVERS):
            is_multi = True
            if serializers.SERVER_TYPE in data and serializers.ENVIRONMENT_NAME in data:
                server_type = ServerTypes.getByName(data.get(serializers.SERVER_TYPE))
                if server_type == None:
                    return {'error': "Failed to find server type " + data.get(serializers.SERVER_TYPE)},is_multi
                environment = Environments.objects.filter(environment=data.get(serializers.ENVIRONMENT_NAME).strip()).first()
                if not environment:
                    return {'error': "Environment name is invalid " + data.get(serializers.ENVIRONMENT_NAME)},is_multi
                servers = Servers.objects.filter(server_type=server_type, environment_id=environment)
                if servers.exists():
                    for server in servers:
                        server_id_list.append(str(server.id))
                    data[serializers.SERVER_IDS] = server_id_list
                else:
                    return {'error': ("Failed to find servers under type %s env %s" %(data.get(serializers.SERVER_TYPE),data.get(serializers.ENVIRONMENT_NAME)))},is_multi
            else:
                return {'error': ("%s or %s is not provided "  % (serializers.SERVER_TYPE, serializers.ENVIRONMENT_NAME))},is_multi
        return error_response,is_multi
    def fillIds(self, request):   
        error_response = None
        data=request.data
        if serializers.SERVER_NAME in data and serializers.SERVER_ID not in data:
            server = Servers.objects.filter(server_name=data.get(serializers.SERVER_NAME).strip()).first()
            if server:
                data[serializers.SERVER_ID] = server.id
            else:
                return {'error': "Server name is invalid"}, status.HTTP_400_BAD_REQUEST 
        if not serializers.SERVER_ID in data:
            return {'error': "Must provide server id"}, status.HTTP_400_BAD_REQUEST 
        if (serializers.SERVER_NAME in data or serializers.ENVIRONMENT_NAME in data or serializers.FILE in data or serializers.CONFIG in data 
            or serializers.ELEMENT_PATH in data or serializers.ATTRIBUTE in data):
            field_id, error_response = getUniqueFieldId(data)
            if field_id:
                data[serializers.FIELD_ID] = field_id
            else:
                return error_response,status.HTTP_400_BAD_REQUEST
            if serializers.USER_NAME in data:
                if len(CurrentLocks.objects.filter(field_id=data.get(serializers.FIELD_ID), is_complete=0, user_id__login=data.get(serializers.USER_NAME).strip(), is_cancelled=0, server_id=data.get(serializers.SERVER_ID))) > 0 :
                    return {'error': "New request is blocked if the previous one with same user, server name, config still being processed."} ,status.HTTP_400_BAD_REQUEST
        if serializers.FIELD_ID in data and serializers.FIELD_ID in field_delay_map:
            latest_timestamp = field_delay_map.get(serializers.FIELD_ID)
            if (datetime.datetime.now() - latest_timestamp).total_seconds() < 11 :
                error_response = {'warning': "There are multiple post requests to add same config in less than 10 seconds, please make sure you are not posting duplicated requests then try again 10 seconds later."}
                return error_response, status.HTTP_429_TOO_MANY_REQUESTS       
        if serializers.USER_NAME in data:
            user = GdUser.objects.filter(login=data.get(serializers.USER_NAME).strip()).first()
            if user:
                if user.login == "qa_test_automation":
                    try:
                        remote_ip = request.META['REMOTE_HOST']
                        if not 'jenk' in socket.gethostbyaddr(remote_ip)[0]:
                            return {'error': "Not allowed to use shared account to make request, please use your private account."}, status.HTTP_400_BAD_REQUEST
                    except Exception as e:
                        return {'error': "Couldn't determine client IP due to exception:  " + str(e)}, status.HTTP_400_BAD_REQUEST
                data[serializers.USER_ID] = user.id
            else:
                return {'error': "User name is invalid"}, status.HTTP_400_BAD_REQUEST
        if serializers.ENVIRONMENT_NAME in data:
            environment = Environments.objects.filter(environment=data.get(serializers.ENVIRONMENT_NAME).strip()).first()
            if environment:
                data[serializers.ENVIRONMENT_ID] = environment.id
            else:
                return {'error': "Environment name is invalid"}, status.HTTP_400_BAD_REQUEST  
        if serializers.VALUE_TYPE in data:
            value_type = ValueTypes.objects.filter(value_type=data.get(serializers.VALUE_TYPE).strip().upper()).first()
            if value_type:
                data[serializers.VALUE_TYPE] = value_type.id
            else:
                return {'error': "Value type is invalid"}, status.HTTP_400_BAD_REQUEST  
            
        return error_response, status.HTTP_200_OK
    def getCurrentLocksByFilters(self, request):   
        error_response = None
        data=request.GET
        currentLocks = CurrentLocks.objects.all()
        is_active = data.get(serializers.IS_ACTIVE,None)
        is_complete = data.get(serializers.IS_COMPLETE,None)
        is_cancelled = data.get(serializers.IS_CANCELLED,None)
        value = data.get(serializers.VALUE,None)
        
        if (serializers.SERVER_NAME in data or serializers.ENVIRONMENT_NAME in data or serializers.FILE in data or serializers.CONFIG in data
        or serializers.ELEMENT_PATH in data or serializers.ATTRIBUTE in data):
            field_id, error_response = getUniqueFieldId(data)
        else:
            field_id = (request.GET.get(serializers.FIELD_ID) if serializers.FIELD_ID in request.GET else None)
         
        user_id = None
        if serializers.USER_NAME in data:
            user = GdUser.objects.filter(login=data.get(serializers.USER_NAME).strip()).first()
            if user:
                user_id = user.id
            else:
                return {'error': "User name is invalid"},currentLocks 
        elif serializers.USER_ID in request.GET and request.GET.get(serializers.USER_ID) != '':
            user_id=request.GET.get(serializers.USER_ID).strip()
            
        env_id = None   
        if serializers.ENVIRONMENT_NAME in data:
            environment = Environments.objects.filter(environment=data.get(serializers.ENVIRONMENT_NAME).strip()).first()
            if environment:
                env_id = environment.id
            else:
                return {'error': "Environment name is invalid"},currentLocks   
        elif serializers.ENVIRONMENT_ID in request.GET and request.GET.get(serializers.ENVIRONMENT_ID) != '':
            env_id = request.GET.get(serializers.ENVIRONMENT_ID).strip()
                               
        if user_id:
            currentLocks = currentLocks.filter(user_id=user_id)
        if field_id:
            currentLocks = currentLocks.filter(field_id=field_id)
        if env_id:
            currentLocks = currentLocks.filter(environment_id=env_id)         
        if is_active:
            currentLocks = currentLocks.filter(is_active=StrUtil.str_to_bool(is_active))
        if is_complete:
            currentLocks = currentLocks.filter(is_complete=StrUtil.str_to_bool(is_complete))
        if is_cancelled:
            currentLocks = currentLocks.filter(is_cancelled=StrUtil.str_to_bool(is_cancelled))   
        if value:
            currentLocks = currentLocks.filter(value=value) 
        return error_response,currentLocks    

class CurrentLocksDetail(APIView):
    """
    Retrieve, update or delete a CurrentLock instance.
    """

    def get(self, request, pk, format=None):
        currentLock = get_object(pk, APP_LABEL,CURRENTLOCKS)
        serializer = serializers.CurrentLocksSerializer(currentLock)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        currentLock = get_object(pk, APP_LABEL,CURRENTLOCKS)
        serializer = serializers.CurrentLocksSerializer(currentLock, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        currentLock = get_object(pk, APP_LABEL,CURRENTLOCKS)
        currentLock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ServersList(APIView):
    """
    List all Servers.
    """  
    def get(self, request, format=None):
        servers = Servers.objects.all()
        if serializers.SERVER_NAME in request.GET and request.GET.get(serializers.SERVER_NAME) != '':
            servers = servers.filter(server_name__iexact=request.GET.get(serializers.SERVER_NAME).strip())
        if serializers.SERVER_TYPE in request.GET:
            servers = servers.filter(server_type=request.GET.get(serializers.SERVER_TYPE).strip())
        if serializers.ENVIRONMENT_NAME in request.GET:
            servers = servers.filter(environment_id__environment__iexact=request.GET.get(serializers.ENVIRONMENT_NAME).strip())
        if serializers.SERVER_TYPE_NAME in request.GET:
            server_type_obj = None
            for st in ServerTypes.objects.all():
                if request.GET.get(serializers.SERVER_TYPE_NAME).strip().upper() == str(st):
                    server_type_obj = st
                    break
            servers = servers.filter(server_type=server_type_obj)

        serializer = serializers.ServersSerializer(servers, many=True)
        return Response(serializer.data)

class ServersDetail(APIView):
    """
    Retrieve a Server instance.
    """
    
    def get(self, request, pk, format=None):
        server = get_object(pk, APP_LABEL,SERVERS)
        serializer = serializers.ServersSerializer(server)
        return Response(serializer.data)
    
class UsersList(APIView):
    """
    List all Users.
    """
    def get(self, request, format=None):
        users = GdUser.objects.all()
        if serializers.LOGIN in request.GET and request.GET.get(serializers.LOGIN) != '':
            users = users.filter(login=request.GET.get(serializers.LOGIN).strip())
        serializer = serializers.UsersSerializer(users, many=True)
        return Response(serializer.data)

class UsersDetail(APIView):
    """
    Retrieve a User instance.
    """  
    def get(self, request, pk, format=None):
        user = get_object(pk, APP_LABEL,GDUSER)
        serializer = serializers.UsersSerializer(user)
        return Response(serializer.data)
    
class FieldsList(APIView):
    """
    List all Fields.
    """
    def get(self, request, format=None):
        fields = (Fields.objects.all() if len(request.GET) != 0 else Fields.objects.all()[:50])
    
        filemaps = None;
        include_filemaps = False;
        if serializers.FILENAME in request.GET and request.GET.get(serializers.FILENAME) != '':
            filemaps = Filemap.objects.filter(filename__iexact=request.GET.get(serializers.FILENAME).strip())
            include_filemaps = True;
        else:
            filemaps = Filemap.objects.all()
            
        if serializers.LOCATION in request.GET and request.GET.get(serializers.LOCATION) != '': 
            include_filemaps = True;
            filemaps = filemaps.filter(location__iexact=request.GET.get(serializers.LOCATION).strip()) 
                   
        if serializers.SERVER_NAME in request.GET and request.GET.get(serializers.SERVER_NAME) != '':
            server = Servers.objects.filter(server_name__iexact=request.GET.get(serializers.SERVER_NAME).strip()).first()
            include_filemaps = True;
            filemaps = filemaps.filter(server_type=(server.server_type if server else None))
                
        if include_filemaps:
            fields = fields.filter(file_id__in=filemaps)
  
                        
        if serializers.FILE_ID in request.GET and request.GET.get(serializers.FILE_ID) != '':
            fields = fields.filter(file_id=request.GET.get(serializers.FILE_ID).strip())
        if serializers.ELEMENT_PATH in request.GET and request.GET.get(serializers.ELEMENT_PATH) != '':
            fields = fields.filter(element_path=request.GET.get(serializers.ELEMENT_PATH).strip())
        if serializers.ATTRIBUTE in request.GET and request.GET.get(serializers.ATTRIBUTE) != '':
            fields = fields.filter(attribute=request.GET.get(serializers.ATTRIBUTE).strip())
        if serializers.PARENT_ID in request.GET and request.GET.get(serializers.PARENT_ID) != '':
            fields = fields.filter(parent_id=request.GET.get(serializers.PARENT_ID).strip())
        if serializers.NAMESPACE in request.GET and request.GET.get(serializers.NAMESPACE) != '':
            fields = fields.filter(namespace=request.GET.get(serializers.NAMESPACE).strip())
        if serializers.DISPLAY in request.GET and request.GET.get(serializers.DISPLAY) != '':
            fields = fields.filter(display__icontains=request.GET.get(serializers.DISPLAY).strip())
        serializer = serializers.FieldsSerializer(fields, many=True)
        return Response(serializer.data)
    
class FieldsDetail(APIView):
    """
    Retrieve a Field instance.
    """
      
    def get(self, request, pk, format=None):
        field = get_object(pk, APP_LABEL,FIELDS)
        serializer = serializers.FieldsSerializer(field)
        return Response(serializer.data)
    
class EnvironmentsList(APIView):
    """
    List all Environments.
    """
    def get(self, request, format=None):
        environments = Environments.objects.all()
        if serializers.ENVIRONMENT in request.GET and request.GET.get(serializers.ENVIRONMENT) != '':
            environments = environments.filter(environment=request.GET.get(serializers.ENVIRONMENT).strip())
            
        serializer = serializers.EnvironmentsSerializer(environments, many=True)
        return Response(serializer.data)
    
class EnvironmentsDetail(APIView):
    """
    Retrieve a Environment instance.
    """     
    def get(self, request, pk, format=None):
        environment = get_object(pk, APP_LABEL,ENVIRONMENTS)
        serializer = serializers.EnvironmentsSerializer(environment)
        return Response(serializer.data)
ENV_DNS_MAP = {
               "AWS_QA":"bossvc.qa.uw2.gdotawsnp.com", "AWS_PI":"bossvc.pie.uw2.gdotawsnp.com"
               }
class EnvironmentsColorStack(APIView):
    """
    Retrieve a Environment instance.
    """     
    @staticmethod
    def get_env_color(env_name): 
        color_stack = "N/A"
        if env_name.upper() not in ENV_DNS_MAP:
            color_stack = "Only env names %s are supported" % ", ".join(ENV_DNS_MAP.keys())
        else:       
            address = ENV_DNS_MAP.get(env_name.upper())
            answers = resolver.query(address, 'CNAME')
            for rdata in answers:
                if "-g." in str(rdata.target):
                    color_stack = "green"
                elif "-b." in str(rdata.target):
                    color_stack = "blue"
                else:
                    color_stack = "N/A"
        return color_stack
    
    def get(self, request, env_name, format=None):
        return Response({"color_stack": EnvironmentsColorStack.get_env_color(env_name)})
       
class FilemapsList(APIView):
    """
    List all Filemaps.
    """
    def get(self, request, format=None):
        filemaps = Filemap.objects.all()
        if serializers.FILENAME in request.GET and request.GET.get(serializers.FILENAME) != '':
            filemaps = filemaps.filter(filename=request.GET.get(serializers.FILENAME).strip())
        if serializers.LOCATION in request.GET and request.GET.get(serializers.LOCATION) != '':
            filemaps = filemaps.filter(location=request.GET.get(serializers.LOCATION).strip())   
        if serializers.SERVER_TYPE in request.GET and request.GET.get(serializers.SERVER_TYPE) != '':
            filemaps = filemaps.filter(server_type=request.GET.get(serializers.SERVER_TYPE).strip()) 
        serializer = serializers.FilemapsSerializer(filemaps, many=True)
        return Response(serializer.data)
    
class FilemapsDetail(APIView):
    """
    Retrieve a Filemap instance.
    """     
    def get(self, request, pk, format=None):
        filemap = get_object(pk, APP_LABEL,FILEMAP)
        serializer = serializers.FilemapsSerializer(filemap)
        return Response(serializer.data)
    
class ServerTypesList(APIView):
    """
    List all ServerTypes.
    """
    def get(self, request, format=None):
        serverTypes = ServerTypes.objects.all()
        if serializers.SERVER_TYPE in request.GET and request.GET.get(serializers.SERVER_TYPE) != '':
            serverTypes = serverTypes.filter(server_type=request.GET.get(serializers.SERVER_TYPE).strip())
            
        serializer = serializers.ServerTypesSerializer(serverTypes, many=True)
        return Response(serializer.data)
    
class ServerTypesDetail(APIView):
    """
    Retrieve a ServerType instance.
    """     
    def get(self, request, pk, format=None):
        serverType = get_object(pk, APP_LABEL,SERVERTYPES)
        serializer = serializers.ServerTypesSerializer(serverType)
        return Response(serializer.data)

class SuspendActivityList(APIView):
    """
    List all ServerTypes.
    """
    def get(self, request, format=None):
        suspendActivities = SuspendActivity.objects.all()
        if serializers.ENVIRONMENT in request.GET and request.GET.get(serializers.SERVER_TYPE) != '':
            suspendActivities = suspendActivities.filter(environment_id__environment__iexact=request.GET.get(serializers.ENVIRONMENT).strip())
            
        serializer = serializers.SuspendActivitySerializer(suspendActivities, many=True)
        return Response(serializer.data)
    
class SuspendActivityDetail(APIView):
    """
    Retrieve a ServerType instance.
    """     
    def get(self, request, pk, format=None):
        suspendActivity = get_object(pk, APP_LABEL,SUSPENDACTIVITY)
        serializer = serializers.SuspendActivitySerializer(suspendActivity)
        return Response(serializer.data)
 