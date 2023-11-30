from django.conf.urls import url
from . import views


urlpatterns = [ # /case_report/
                url(r'^$', views.CaseView.as_view(), name='case_report'),
                url(r'^download_case_report$', views.download_case_report, name='download_case_report'),
                url(r'^get_progress/$', views.getProgress, name='case_report_get_progress'),
                url(r'^cancel_progress/$', views.cancelProgress, name='case_report_cancel_progress'),
              ]