from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from datetime import datetime
from datetime import timedelta
from calendar import weekday
from common_utils.str_util import StrUtil

INPUT_DATE = 'input_date'
DAY_INTERVALS = 'day_intervals'
SKIP_WEEKEND = 'skip_weekend'
SKIP_HOLIDAY = 'skip_holiday'
NEXT_BUSINESS_DATE = 'next_business_date'
YEAR = 'year'
NAME = 'name'
DATE = 'date'
HOLIDAY_CALENDAR = 'holiday_calendar'

def getHolidays(year):
    holidays = {}
    holidays['NEW_YEARS_DAY'] = datetime.strftime(getNewYearsDay(year), '%Y-%m-%d')
    holidays['MLK_DAY'] = datetime.strftime(getMLKDay(year), '%Y-%m-%d')
    holidays['PRESIDENTS_DAY'] = datetime.strftime(getPresidentsDay(year), '%Y-%m-%d')
    holidays['MEMORIAL_DAY'] = datetime.strftime(getMemorialDay(year), '%Y-%m-%d')
    holidays['INDEPENDENCE_DAY'] = datetime.strftime(getIndependenceDay(year), '%Y-%m-%d')
    holidays['LABOR_DAY'] = datetime.strftime(getLaborDay(year), '%Y-%m-%d')
    holidays['COLUMBUS_DAY'] = datetime.strftime(getColumbusDay(year), '%Y-%m-%d')
    holidays['VETERANS_DAY'] = datetime.strftime(getVetsDay(year), '%Y-%m-%d')
    holidays['THANKSGIVING_DAY'] = datetime.strftime(getTurkeyDay(year), '%Y-%m-%d')
    holidays['CHRISTMAS_DAY'] = datetime.strftime(getChristmasDay(year), '%Y-%m-%d')
    return holidays

def getNewYearsDay(year):
    nyDate = datetime(year,1,1)
    if nyDate.isoweekday() == 7:
        nyDate += timedelta(days=1)
    return nyDate.date()


def getMLKDay(year):
    mlkDate = datetime(year, 1, 15) #Earliest Date that MLK day can be.
    while mlkDate.isoweekday() != 1:
        mlkDate += timedelta(days=1)
    return mlkDate.date()

def getPresidentsDay(year):
    potusDate = datetime(year, 2, 15) #Earliest Date that President's day can be
    while potusDate.isoweekday() != 1:
        potusDate += timedelta(days=1)
    return potusDate.date()

def getMemorialDay(year):
    memDate = datetime(year, 5, 31)
    while memDate.isoweekday() != 1:
        memDate += timedelta(days=1)
    return memDate.date()

def getIndependenceDay(year):
    indDate = datetime(year, 7, 4)
    if indDate.isoweekday() == 7:
        indDate += timedelta(days=1)
    return indDate.date()

def getLaborDay(year):
    laborDate = datetime(year, 9, 1) #Earliest Date that labor day can be
    while laborDate.isoweekday() != 1:
        laborDate += timedelta(days=1)
    return laborDate.date()

def getColumbusDay(year):
    colDate = datetime(year, 10, 8) #Earliest Date that columbus day can be
    while colDate.isoweekday() != 1:
        colDate += timedelta(days=1)
    return colDate.date()

def getVetsDay(year):
    vetsDate = datetime(year, 11, 11)
    if vetsDate.isoweekday() == 7:
        vetsDate += timedelta(days=1)
    return vetsDate.date()

def getTurkeyDay(year):
    turkeyDate = datetime(year, 11, 22) #Earliest Date that Thanksgiving day can be
    while turkeyDate.isoweekday() != 4:
        turkeyDate += timedelta(days=1)
    return turkeyDate.date()

def getChristmasDay(year):
    xmasDate = datetime(year, 12, 25)
    if xmasDate.isoweekday() == 7:
        xmasDate += timedelta(days=1)
    return xmasDate.date()

class BusinessDayCalculator(APIView):
    """
    Retrieve the next business day.
    """
    def get(self, request, format=None):
        error_response, responseData = self.getNextBusinessDayByFilters(request)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.BusinessDaySerializer(responseData, many=False)
        return Response(serializer.data)

    def getNextBusinessDayByFilters(self, request):
        error_response = None
        responseData = {}
        data=request.GET
        
        input_date = data.get(serializers.INPUT_DATE, datetime.strftime(datetime.now(),'%Y-%m-%d'))
        responseData[INPUT_DATE] = input_date
        day_intervals = data.get(serializers.DAY_INTERVALS,1)
        responseData[DAY_INTERVALS] = day_intervals
        skip_weekend = data.get(serializers.SKIP_WEEKEND,True)
        responseData[SKIP_WEEKEND] = skip_weekend
        skip_holiday = data.get(serializers.SKIP_HOLIDAY,True)
        responseData[SKIP_HOLIDAY] = skip_holiday
        
        tmpDate = datetime.strptime(input_date,'%Y-%m-%d')
        nextBusinessDay = self.getBusinessDaySkippingWeekendsAndHolidays(tmpDate, StrUtil.str_to_bool(skip_weekend), StrUtil.str_to_bool(skip_holiday), int(day_intervals))

        responseData[NEXT_BUSINESS_DATE] = datetime.strftime(nextBusinessDay,'%Y-%m-%d')
        return error_response, responseData

    def getBusinessDaySkippingWeekendsAndHolidays(self, from_date, if_skip_weekend, if_skip_holiday, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5 and if_skip_weekend: #sunday = 6
                continue
            if datetime.strftime(current_date,'%Y-%m-%d') in getHolidays(current_date.year).values() and if_skip_holiday:
                continue
            business_days_to_add -= 1
        return current_date

class HolidayCalendar(APIView):
    """
    Retrieve the holiday calendar.
    """
    def get(self, request, format=None):
        error_response, responseData = self.getHolidayCalendar(request)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.HolidaySerializer(responseData, many=False)
        return Response(serializer.data)
    
    def getHolidayCalendar(self, request):
        error_response = None
        responseData = {}
        holidayData = []
        data=request.GET
        year = data.get(serializers.YEAR, datetime.now().year)
        responseData[YEAR] = str(year)
        
        for key, value in getHolidays(int(year)).items():
            singleHoliday = {}
            singleHoliday[NAME] = key
            singleHoliday[DATE] = value
            holidayData.append(singleHoliday)
        responseData[HOLIDAY_CALENDAR] = holidayData
        return error_response, responseData     