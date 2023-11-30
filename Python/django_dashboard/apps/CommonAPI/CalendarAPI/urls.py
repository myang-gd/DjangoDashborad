from django.conf.urls import url
from .import views

urlpatterns = [
        url(r'^next-business-day/$', views.BusinessDayCalculator.as_view()),
        url(r'^holiday-calendar/$', views.HolidayCalendar.as_view()),
    ]