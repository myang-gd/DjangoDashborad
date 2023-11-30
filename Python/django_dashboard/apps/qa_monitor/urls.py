from django.conf.urls import url
from apps.qa_monitor import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
        url(r'^$', login_required(views.schedule_monitor), name='monitor'),
        url(r'^schedule_monitor/$', login_required(views.schedule_monitor), name='schedule_monitor'),
        url(r'^view_monitors/$', login_required(views.view_monitors), name='view_monitors'),
        url(r'^view_runs/$', login_required(views.view_runs), name='view_runs'),
        url(r'^monitor_run_result/$', login_required(views.monitor_run_result) , name='monitor_run_result'),
        url(r'^viewRequest/$', login_required(views.requestPopUp) , name='view_monitor_request'),
        url(r'^viewResponse/$', login_required(views.responsePopUp) , name='view_monitor_response'),
    ]