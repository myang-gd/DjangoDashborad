from rest_framework import serializers

PROJECT_NAME = 'project_name'
BASE_LINE_DATE = 'base_line_date'
MILESTONE = 'milestone'

class CurrentSprintDetailSerializer(serializers.Serializer):
    project_name = serializers.CharField(allow_null=False, required=True, max_length=50)
    base_line_date = serializers.DateTimeField(allow_null=True, required=False)
    milestone = serializers.CharField(allow_null=True, required=True, max_length=50)
    sprint_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint1_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint2_date = serializers.DateTimeField(allow_null=True, required=False)
    hardening_date = serializers.DateTimeField(allow_null=True, required=False)
    pie_date = serializers.DateTimeField(allow_null=True, required=False)
    release_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint_state = serializers.CharField(allow_null=True, required=False, max_length=50)

class SpecificSprintInfoSerializer(serializers.Serializer):
    project_name = serializers.CharField(allow_null=False, required=True, max_length=50)
    milestone = serializers.CharField(allow_null=True, required=True, max_length=50)
    sprint_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint1_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint2_date = serializers.DateTimeField(allow_null=True, required=False)
    hardening_date = serializers.DateTimeField(allow_null=True, required=False)
    pie_date = serializers.DateTimeField(allow_null=True, required=False)
    release_date = serializers.DateTimeField(allow_null=True, required=False)

class CustomListItemSerializer(serializers.Serializer):
    milestone = serializers.CharField(allow_null=True, required=True, max_length=50)
    sprint_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint1_date = serializers.DateTimeField(allow_null=True, required=False)
    sprint2_date = serializers.DateTimeField(allow_null=True, required=False)
    hardening_date = serializers.DateTimeField(allow_null=True, required=False)
    pie_date = serializers.DateTimeField(allow_null=True, required=False)
    release_date = serializers.DateTimeField(allow_null=True, required=False)
    
class SprintListSerializer(serializers.Serializer):
    project_name = serializers.CharField(allow_null=False, required=True, max_length=50)
    base_line_date = serializers.DateTimeField(allow_null=True, required=False)
    milestone_list = CustomListItemSerializer(many=True)