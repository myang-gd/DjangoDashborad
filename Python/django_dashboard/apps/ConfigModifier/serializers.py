from rest_framework import serializers
from .models import CurrentLocks,GdUser,Fields,Environments,Servers,Filemap,ServerTypes,FieldValues,SuspendActivity,ValueTypes
from django.core.exceptions import ValidationError
from datetime import datetime
from . import models

IS_ACTIVE = 'is_active'
IS_CANCELLED = 'is_cancelled'
IS_COMPLETE = 'is_complete' 
REQUESTTIME = 'requesttime' 
STARTDATE = 'startdate' 
VALUE = 'value' 
DURATION = 'duration' 
USER_ID = 'user_id' 
USER_NAME = 'user_name' 
FIELD_ID = 'field_id'
ENVIRONMENT_ID = 'environment_id' 
SERVER_ID = 'server_id'
ENVIRONMENT_NAME = 'environment_name' 
VALUE_TYPE = 'value_type'
INCLUDE_ALL_SERVERS = 'include_all_servers'  
SERVER_IDS = 'server_ids'

SERVER_NAME = 'server_name'
SERVER_TYPE = 'server_type'
SERVER_TYPE_NAME = 'server_type_name'
LOGIN = 'login'
FILE_ID = 'file_id'
ELEMENT_PATH = 'element_path'
ATTRIBUTE = 'attribute'
PARENT_ID = 'parent_id'
NAMESPACE = 'namespace'
DISPLAY = 'display'
ENVIRONMENT = 'environment'
FILENAME = 'filename'
LOCATION = 'location'
FILE = 'file'
CONFIG = 'config'

def validate_cancel(**kwargs):
        is_active = kwargs.pop(IS_ACTIVE)
        is_cancelled = kwargs.pop(IS_CANCELLED)
            
        if is_cancelled == True and is_active == True:
            raise ValidationError("Can not cancel active request")
def validate_duration(**kwargs):
        is_active = kwargs.pop(IS_ACTIVE)
        is_cancelled = kwargs.pop(IS_CANCELLED)
        is_complete = kwargs.pop(IS_COMPLETE)
        if is_active == False or is_cancelled == True or is_complete == True:
            raise ValidationError("Can not set duration for request in completed/canceled status")
        
def getServerIdByFieldandEnv(field, environment):       
        server_id = None
        if field and field.file_id and field.file_id.server_type:
            server = Servers.objects.filter(server_type=field.file_id.server_type, environment_id=environment).first()
            if server:
                server_id = server.id
        
        return   server_id   
                 
def getFields(**kwargs):   
        server_name = kwargs.pop(SERVER_NAME,None)
        file_name = kwargs.pop(FILENAME,None)    
        location = kwargs.pop(LOCATION,None)   
        display = kwargs.pop(DISPLAY,None)    
        element_path = kwargs.pop(ELEMENT_PATH,None)    
        attribute = kwargs.pop(ATTRIBUTE,None) 
        
        fields = Fields.objects.all()
    
        filemaps = None;
        include_filemaps = False;
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
                
        if include_filemaps:
            fields = fields.filter(file_id__in=filemaps)            
        if display:
            fields = fields.filter(display__icontains=display.strip()) 
        if element_path:
            fields = fields.filter(element_path=element_path.strip()) 
        if attribute:
            fields = fields.filter(attribute=attribute.strip()) 

        return  fields
    
def getUniqueFieldId(**kwargs):         
    kwargs_copy = kwargs
    
    server_name = kwargs_copy.pop(SERVER_NAME,None)
    environment_name = kwargs_copy.pop(ENVIRONMENT_NAME,None)
    
    if server_name and environment_name:
        server = Servers.objects.filter(server_name=server_name).first()
        if server and server.environment_id != environment_name.strip():
            raise ValidationError("Server and environment name does not match")        
    fields = getFields(kwargs)
    
    if len(fields) == 0:
        raise ValidationError("Can't find field") 
    if len(fields) != 1:
        raise ValidationError("Can't find unique field") 
    
    return fields.first().id
def checkValue(value, field_id):
        fieldValues = FieldValues.objects.filter(field_id=field_id)
        if fieldValues and value:
            if value.strip() not in [fieldValue.field_value for fieldValue in fieldValues]:
                raise ValidationError("Value is invalid") 
    
def getUniqueFieldIdByAttrs(attrs):         
    server_name = attrs.get(SERVER_NAME)
    environment_name = attrs.get(ENVIRONMENT_NAME)
    filename = attrs.get(FILENAME)   
    location = attrs.get(LOCATION) 
    display = attrs.get(DISPLAY)   
    element_path = attrs.get(ELEMENT_PATH) 
    attribute = attrs.get(ATTRIBUTE)
    
    return getUniqueFieldId(server_name=server_name,environment_name=environment_name,
                          filename=filename,location=location,display=display,element_path=element_path,attribute=attribute)




class CurrentLocksSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    value = serializers.CharField(max_length=models.FIELD_VALUE_MAX)
    duration = serializers.IntegerField(max_value=2147483647, min_value=1)
    startdate = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    requesttime = serializers.DateTimeField(allow_null=True, required=False)
    user_id = serializers.PrimaryKeyRelatedField(queryset=GdUser.objects.all(),required=False)
    field_id = serializers.PrimaryKeyRelatedField(queryset=Fields.objects.all())
    environment_id = serializers.PrimaryKeyRelatedField(queryset=Environments.objects.all())
    is_active = serializers.BooleanField(required=False, read_only=True, default=False)
    is_complete = serializers.BooleanField(required=False, read_only=True, default=False)
    is_cancelled = serializers.BooleanField(required=False)
    server_id = serializers.PrimaryKeyRelatedField(queryset=Servers.objects.all())
    value_type = serializers.PrimaryKeyRelatedField(queryset=ValueTypes.objects.all(),required=False)
    
    def create(self, validated_data):
        """
        Create and return a new `CurrentLock` instance, given the validated data.
        """
        if IS_CANCELLED not in validated_data:
            validated_data[IS_CANCELLED] = False;
        if REQUESTTIME not in validated_data:
            validated_data[REQUESTTIME] = datetime.now();
        
        return CurrentLocks.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `CurrentLock` instance, given the validated data.
        """
        instance.value = validated_data.get(VALUE, instance.value)
        instance.duration = validated_data.get(DURATION, instance.duration)
        instance.startdate = validated_data.get(STARTDATE, instance.startdate)
        instance.requesttime = validated_data.get(REQUESTTIME, instance.requesttime)
        instance.user_id = validated_data.get(USER_ID, instance.user_id)
        instance.field_id = validated_data.get(FIELD_ID, instance.field_id)
        instance.environment_id = validated_data.get(ENVIRONMENT_ID, instance.environment_id)
        instance.is_active = validated_data.get(IS_ACTIVE, instance.is_active)
        instance.is_complete = validated_data.get(IS_COMPLETE, instance.is_complete)
        instance.is_cancelled = validated_data.get(IS_CANCELLED, instance.is_cancelled)
        instance.server_id = validated_data.get(SERVER_ID, instance.server_id)
        instance.save()
        return instance
   
    def validate(self, attrs):
       
        if self.instance:
            if (USER_ID,FIELD_ID,ENVIRONMENT_ID,VALUE,STARTDATE,REQUESTTIME) in attrs:
                raise ValidationError("Not allowed to update %s/%s/%s/%s/%s/%s" % (USER_ID,FIELD_ID,ENVIRONMENT_ID,VALUE,STARTDATE, REQUESTTIME))
            
            is_cancelled_ins = self.instance.is_cancelled
            is_complete_ins = self.instance.is_complete
            is_active_ins = self.instance.is_active
                           
            if IS_CANCELLED in attrs:
                is_active_ins = self.instance.is_active
                is_cancelled = attrs[IS_CANCELLED]
                if is_cancelled == True and not is_complete_ins and not is_cancelled_ins:
                    if is_active_ins:
                        attrs[DURATION] = 1
                        attrs.pop(IS_CANCELLED) 
                elif is_cancelled == False :
                    raise ValidationError("Not allowed to update is_cancelled to false")
            
                    
            elif DURATION in attrs:
                is_cancelled_ins = self.instance.is_cancelled
                is_complete_ins = self.instance.is_complete
                is_active_ins = self.instance.is_active
                validate_duration(is_cancelled=is_cancelled_ins,is_complete=is_complete_ins,is_active=is_active_ins)
        else:
            if IS_CANCELLED in attrs:  
                raise ValidationError("Not allowed to set %s" %(IS_CANCELLED))
#             if SERVER_ID in attrs and SERVER_NAME in attrs:
#                 raise ValidationError("Server id can't be used with server name")
#             if USER_ID  in attrs and USER_NAME in attrs:
#                 raise ValidationError("User id can't be used with server name")
#             elif USER_NAME in attrs:
#                 user = GdUser.objects.filter(login=attrs.get(USER_NAME).strip()).first()
#                 if user:
#                     attrs[USER_ID] = user
#                     attrs.pop(USER_NAME)
#                 else:
#                     raise ValidationError("User name is invalid")
#             if FIELD_ID in attrs and (SERVER_NAME or FILENAME or LOCATION or DISPLAY or ELEMENT_PATH or ATTRIBUTE) in attrs:
#                 raise ValidationError("Field_id can't be used with (%s,%s,%s,%s,%s,%s)" %(SERVER_NAME,FILENAME,LOCATION,DISPLAY,ELEMENT_PATH,ATTRIBUTE))
#             if (FIELD_ID and ENVIRONMENT_ID) in attrs:            
#                 server_id = getServerIdByFieldandEnv(attrs.get(FIELD_ID), attrs.get(ENVIRONMENT_ID))
 
            if SERVER_NAME in attrs:
                server = Servers.objects.filter(server_name=attrs.get(SERVER_NAME).strip()).first()
                server_id = (server.id if server else None)
                if not server_id:
                    raise ValidationError("Failed to find server based server_name: %s" %(str(attrs.get(SERVER_NAME))))
            
                if SERVER_ID in attrs and attrs.get(SERVER_ID) != server_id:
                    raise ValidationError("Provided server id:(%s) does not match expected value (%s) based on inputs field_id (%s) environment_id (%s)"  %(str(attrs.get(SERVER_ID)),
                                                                                                                                                                str(server_id),  
                                                                                                                                                                str(attrs.get(FIELD_ID).id), 
                                                                                                                                                               str(attrs.get(ENVIRONMENT_ID).id),
                                                                                                                                                                   
                                                                                                                                                                   )
                                              )
                elif SERVER_ID not in attrs:
                    attrs[SERVER_ID] = server_id
            if FIELD_ID not in attrs:
                field_id = getUniqueFieldIdByAttrs(attrs)
                if field_id:
                    attrs[FIELD_ID] = field_id
            if VALUE in attrs:       
                checkValue(attrs[VALUE], attrs[FIELD_ID])               
        return attrs

class ServersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servers
        fields = '__all__'
        
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GdUser
        fields = '__all__'
class FieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = '__all__'
class EnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environments
        fields = '__all__'
class FilemapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filemap
        fields = '__all__'
class ServerTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerTypes
        fields = '__all__'
class SuspendActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspendActivity
        fields = '__all__'