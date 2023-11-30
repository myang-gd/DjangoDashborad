from rest_framework import serializers

from apps.query_view.models import QueryScript, Database, Recent, UserProfile


class MyDatabaseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    server = serializers.CharField(required=True, allow_blank=False, max_length=128)
    database = serializers.CharField(required=True, allow_blank=False, max_length=128)
    username = serializers.CharField(required=True, allow_blank=False, max_length=128)
    # password = serializers.CharField(required=True, allow_blank=False, max_length=128)
    conn_properties = serializers.CharField(required=True, allow_blank=False, max_length=128)
    created_by = serializers.CharField(required=True, allow_blank=False, max_length=128)

    def create(self, validated_data):
        """
        Create and return a new `QueryScript` instance, given the validated data.
        """
        return Database.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `QueryScript` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.server = validated_data.get('server', instance.server)
        instance.database = validated_data.get('database', instance.database)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.conn_properties = validated_data.get('conn_properties', instance.conn_properties)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.save()
        return instance


class MyQueryScriptSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, allow_blank=False, max_length=128)
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    sql = serializers.CharField(style={'base_template': 'textarea.html'})
    category = serializers.CharField(required=True, allow_blank=False, max_length=128)
    created_by = serializers.CharField(required=True, allow_blank=False, max_length=128)
    databases =  serializers.CharField(style={'base_template': 'textarea.html'})
    target = serializers.CharField(required=True, allow_blank=False, max_length=128)

    def create(self, validated_data):
        """
        Create and return a new `QueryScript` instance, given the validated data.
        """
        return QueryScript.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `QueryScript` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.sql = validated_data.get('sql', instance.sql)
        instance.category = validated_data.get('category', instance.category)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.save()
        return instance


class MyUserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.CharField(required=True, allow_blank=False, max_length=128)
    profile = serializers.MultipleChoiceField(choices=UserProfile.MY_PROFILE)

    def create(self, validated_data):
        """
        Create and return a new `QueryScript` instance, given the validated data.
        """
        return Recent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `QueryScript` instance, given the validated data.
        """
        instance.profile = validated_data.get('profile', instance.profile)
        instance.created_date = validated_data.get('created_date', instance.created_date)
        instance.query_script = validated_data.get('query_script', instance.query_script)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.save()
        return instance


class MyRecentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    profile = MyUserProfileSerializer()
    created_date = serializers.DateTimeField()
    query_script = MyQueryScriptSerializer()
    parameters = serializers.CharField(required=True, allow_blank=False, max_length=1024)

    def create(self, validated_data):
        """
        Create and return a new `QueryScript` instance, given the validated data.
        """
        return Recent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `QueryScript` instance, given the validated data.
        """
        instance.profile = validated_data.get('profile', instance.profile)
        instance.created_date = validated_data.get('created_date', instance.created_date)
        instance.query_script = validated_data.get('query_script', instance.query_script)
        instance.parameters = validated_data.get('parameters', instance.parameters)
        instance.save()
        return instance