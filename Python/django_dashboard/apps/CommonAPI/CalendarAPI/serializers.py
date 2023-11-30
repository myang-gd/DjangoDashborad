from rest_framework import serializers
from datetime import datetime

INPUT_DATE = 'input_date'
DAY_INTERVALS = 'day_intervals'
SKIP_WEEKEND = 'skip_weekend'
SKIP_HOLIDAY = 'skip_holiday'
YEAR = 'year'

class BusinessDaySerializer(serializers.Serializer):
    input_date = serializers.DateField(allow_null=True, required=False, read_only=True)
    day_intervals = serializers.IntegerField(max_value=2147483647, read_only=True, min_value=1)
    skip_weekend = serializers.BooleanField(required=False, read_only=True, default=True)
    skip_holiday = serializers.BooleanField(required=False, read_only=True, default=True)
    next_business_date = serializers.DateField(allow_null=True, required=False, read_only=True)

class HolidaySerializer(serializers.Serializer):
    year = serializers.DateTimeField(allow_null=True, required=False, read_only=True, default=datetime.strftime(datetime.now(),'%Y'))
    name = serializers.CharField(max_length=5000, allow_null=True, required=False, read_only=True)
    date = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    holiday_calendar = serializers.ListField(allow_null=True, required=False, read_only=True)
